import sys
from argparse import ArgumentParser

from WrappedObjects import ObjectifiedDict, Config, Credential, Beatmap
from utils import NULL, PrettyPrinter, inquire_params, get_date_from_string, load_json, remove_duplicate_in_list

from DBManager import osuDB, MultiThreadedOsuDB
from api import osuAPI


class Interface:
    def __init__(self, config: Config, api_key: str, credentials: Credential):
        self.config = config
        self.api_key = api_key
        self.credentials = credentials
        self.api: osuAPI = osuAPI(self.api_key, self.credentials, self.config, initialize=False)
        self.db: osuDB = MultiThreadedOsuDB(config.database, initialize=False)
        self.printer: PrettyPrinter = PrettyPrinter._get_default()
        self.printer.debug = self.config.debug
        
        self._actions = {'DOWNLOAD':self.cli_downloader}
        
        self.parsed_args = {}
        self.params = {}
        self.filters = {}
    
    @property
    def initialized(self):
        return self.api._logged_in
    
    def _init(self):
        self.db._init()
        self.api._init()

    def process_filter(self, filter_arg_entry):
        processors = {'approved': lambda lst:(lambda lst:lambda q: q in lst)(','.join(lst)),
                      'difficultyrating': lambda _s: (lambda matchf:lambda f: float(f) == matchf)(float(_s)) if not _s.__contains__('-') else 
                                          lambda _s: (lambda bounds: lambda f: bounds[0] <= float(f) <= bounds[1])(sorted(map(float, _s.split('-')))),
                      'favourite_count': lambda _s: (lambda min_count: lambda count: min_count<=int(count))(int(_s)),
                      'rating': lambda _s: (lambda min_rating: lambda rating: min_rating<=float(rating))(float(_s))}
        name, value = filter_arg_entry
        self.filters[name] = self.filters.get(name, []) + [processors.get(name)(value)]
    
    def process_args(self):
        for key, val in [(k,v) for k,v in self.parsed_args.items() if v is not NULL]:
            if key.startswith('config_'):
                self.config[key.split('_', 1)[-1]] = val
            elif key.startswith('params_'):
                self.params[key.split('_', 1)[-1]] = val
            elif key.startswith('filters_'):
                self.process_filter((key.split('_', 1)[-1],val))

    def filter_beatmap(self, beatmap: dict):
        for beatmap_attr, filters in self.filters.items():
            if any([not filter(beatmap[beatmap_attr]) for filter in filters]):
                return False
        return True
    
    def filter_beatmaps(self, beatmap_list: list):
        return [beatmap for beatmap in beatmap_list if self.filter_beatmap(beatmap)]
    
    def start(self, args: list = sys.argv[1:]):
        parser = ArgumentParser(description="This is the cli interface for osu-map-downloader.")
        
        parser.add_argument("action", metavar='ACTION', type=str.upper, choices=self._actions, help="Action to do.")
        
        configs = parser.add_argument_group('Configurations')
        configs.add_argument('--download-directory', metavar='DIRECTORY', dest='config_download_directory', default=NULL, help="Sets download directory for api. Default='./Downloads'")
        configs.add_argument('--download-chunk-size', metavar='CHUNK_SIZE', dest='config_download_chunk_size', type=int, default=self.config.download_chunk_size, help="Sets download chunk size for api. Default=512b")
        configs.add_argument('--record-beatmaps', action='store_true', dest='config_record_beatmaps', default=NULL, help="Whether to save beatmaps to database or not.")
        configs.add_argument('--lookup-in-database', action='store_true', dest='config_lookup_beatmaps_in_database', default=NULL, help="Whether to search for beatmaps to download from accumulated database.")
        configs.add_argument('-d', '--debug', dest='config_debug', default=NULL, action='store_true', help="Sets debug in printer. Default=False")
        
        params = parser.add_argument_group('Download Params')
        params.add_argument('-s', '--since', metavar='DATETIME', dest='params_since', default=NULL, type=get_date_from_string, help="Add get beatmaps param since given date. Supported formats: YYYY-MM-DD, YYYY/MM/DD, DD-MM-YY, DD/MM/YY")
        params.add_argument('-m', '--mode', '--game-mode', metavar='MODE', dest='params_m', default=NULL, help="Add get beatmaps param for game mode. Modes: 0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania")
        params.add_argument('-l', '--limit', metavar='LIMIT', dest='params_limit', default=NULL, help="Adds limit to return beatmaps count. Default=500")
        
        filters = parser.add_argument_group('Download Filters')
        filters.add_argument('-a', '-q', '--approved', '--qualification', metavar='QUALIFICATION', action='append', dest='filters_approved', default=NULL, help="Adds beatmaps filter to specified approved. To add multiple qualifications, stack it like: '-q 0 -q 1 ...'. Qualifications: 4 = loved, 3 = qualified, 2 = approved, 1 = ranked, 0 = pending, -1 = WIP, -2 = graveyard")
        filters.add_argument('--diff', '--difficulty', '--difficulty-rating', metavar='RATING', dest='filters_difficultyrating', default=NULL, help="Adds beatmaps filter for range or exact match on difficultyrating. Ratings will be converted to floats. Rating formats: [x.xx] or [x] and [x.xx-y.yy]")
        filters.add_argument('-f', '--favourite', dest='filters_favourite_count', metavar='FAVOURITE_COUNT', default=NULL, help="Adds beatmaps filter for minimum favourite count on the beatmapset.")
        filters.add_argument('-r', '--rating', dest='filters_rating', metavar='RATING', default=NULL, help="Adds beatmaps filter for minimum rating on the beatmapset.")
        
        namespace = parser.parse_args(args)
        self.parsed_args = ObjectifiedDict(vars(namespace))
        self.process_args()
        
        self.printer.print_debug("Interface.start Process", 
                                 {'Action': namespace.action, 'Params': self.params, 'Debug': self.config.debug, 
                                  'Namespace': namespace, 'Filter Conditions': self.filters},
                                 header_prefix='|>|')
        self.printer.debug = self.config.debug
        
        return self._actions[namespace.action]()
    
    def cli_downloader(self):
        if not self.initialized:
            self._init()
        
        
        beatmaps = self.api.get_beatmaps(params=self.params)
        print("Fetched {} Beatmaps from osu api.".format(len(beatmaps)))
        if self.config.record_beatmaps:
            self.db.add_beatmaps(beatmaps, replace=True)
            print("Recorded {} Beatmaps into the database.".format(len(beatmaps)))
        if self.config.lookup_beatmaps_in_database:
            beatmaps_in_db = self.db.get_all_beatmaps()
            print("Found {} Beatmaps in database.".format(len(beatmaps_in_db)))
        
        filtered_beatmaps = [Beatmap(data) for data in self.filter_beatmaps(beatmaps)]
        beatmapsets = remove_duplicate_in_list(filtered_beatmaps, 'beatmapset_id', lambda e:e['beatmap_id'])
        print("Filtered Beatmaps: {} Beatmaps and {} Unique Beatmapsets".format(len(filtered_beatmaps), len(beatmapsets)))
        
        print("Starting Download...\n")
        
        
        for i, beatmap in enumerate(filtered_beatmaps):
            print("\nBeatmap #{}".format(i+1))
            print("Processing Beatmap: {}".format(str(beatmap)))
            self.printer.print_info('Downloading Process#{}'.format(i+1), 
                                    {'Beatmap Object':repr(beatmap)}, with_header=False)
            if self.db.check_exists_in_downloaded(beatmap):
                print("Already downloaded, entry found in database.\n")
                continue
            print("Downloading Beatmap...")
            self.api.download_to_file(beatmap)
            print("Beatmap Downloaded.\n")
            self.db.flag_as_downloaded(beatmap)
        
        print("Finished Downloading.")
