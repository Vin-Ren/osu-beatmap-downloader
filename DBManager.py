import sqlite3
from threading import Thread
from queue import Queue

from DBModels import Beatmap, DownloadedBeatmapset, Model

from typing import List, Tuple, Dict, Any, Union


dict_factory = lambda cursor, row: {col[0]:row[i] for i, col in enumerate(cursor.description)}


class osuDB:
    TABLES = {'beatmaps': Beatmap, 'downloaded': DownloadedBeatmapset}
    
    def __init__(self, database: str, *, initialize=True):
        self.database = database
        self.connection = sqlite3.connect(database=self.database)
        self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()
        
        if initialize:
            self._init()
    
    def __repr__(self):
        return "<osuDB database='{}'>".format(self.database)
    
    def _init(self):
        for table in self.TABLES.values():
            self.cursor.execute(table.make_query())
            self.connection.commit()
    
    def insert(self, obj: Model, **insertKw):
        self.cursor.execute(*obj.make_insert_args(**insertKw))
        self.connection.commit()
    
    def insert_many(self, list_of_obj: List[Model], **insertKw):
        # Groups each model
        model_groups = {}
        for obj in list_of_obj:
            model_groups[obj.__class__] = model_groups.get(obj.__class__, []) + [obj]
        
        # Groups query string with its execute_many values
        query_groups = {table.make_insert_query(**insertKw) : [obj.make_insert_values() for obj in objs] for table, objs in model_groups.items()}
        
        # Do the execute many process
        for query_string, execute_many_values in query_groups.items():
            self.cursor.executemany(query_string, execute_many_values)
            self.connection.commit() # Commit for every model.
    
    def select(self, obj: Model, **selectKw):
        self.cursor.execute(obj.make_selector_query(**selectKw))
        return self.cursor.fetchall()
    
    def add_beatmap(self, beatmap:Union[Beatmap, dict], **insertKw):
        if isinstance(beatmap, dict):
            beatmap = Beatmap(beatmap)
        self.insert(beatmap, **insertKw)
    
    def add_beatmaps(self, beatmap_list: List[Union[Beatmap, dict]], **insertKw):
        self.insert_many([Beatmap(beatmap) if isinstance(beatmap, dict) else beatmap for beatmap in beatmap_list], **insertKw)
    
    def flag_as_downloaded(self, beatmap_descriptor: Union[Beatmap, DownloadedBeatmapset, dict, int], **insertKw):
        if isinstance(beatmap_descriptor, Beatmap):
            downloaded_object = DownloadedBeatmapset(beatmap_descriptor.data)
        elif isinstance(beatmap_descriptor, DownloadedBeatmapset):
            downloaded_object = beatmap_descriptor
        elif isinstance(beatmap_descriptor, dict):
            downloaded_object = DownloadedBeatmapset({'beatmapset_id':beatmap_descriptor['beatmapset_id'], 'downloaded': True})
        else:
            downloaded_object = DownloadedBeatmapset({'beatmapset_id': int(beatmap_descriptor), 'downloaded': True})
        self.insert(downloaded_object, **insertKw)

    def bulk_flag_as_downloaded(self, beatmap_descriptors: List[Union[Beatmap, DownloadedBeatmapset, dict, int]], **insertKw):
        downloaded_beatmapset_objects = []
        for beatmap_descriptor in beatmap_descriptors:
            if isinstance(beatmap_descriptor, Beatmap):
                downloaded_object = DownloadedBeatmapset(beatmap_descriptor.data)
            elif isinstance(beatmap_descriptor, DownloadedBeatmapset):
                downloaded_object = beatmap_descriptor
            elif isinstance(beatmap_descriptor, dict):
                downloaded_object = DownloadedBeatmapset({'beatmapset_id':beatmap_descriptor['beatmapset_id'], 'downloaded': True})
            else:
                downloaded_object = DownloadedBeatmapset({'beatmapset_id': int(beatmap_descriptor), 'downloaded': True})
            downloaded_beatmapset_objects.append(downloaded_object)
        self.insert_many(downloaded_beatmapset_objects, **insertKw)
        
    def get_all_beatmaps(self):
        self.cursor.execute("SELECT * FROM {0[beatmaps].table_name}".format(self.TABLES))
        return self.cursor.fetchall()
    
    def get_beatmaps(self, beatmap_descriptor: Union[Beatmap, int], **selectKw):
        if isinstance(beatmap_descriptor, int):
            beatmap_descriptor = Beatmap({'beatmap_id':beatmap_descriptor})
        return self.select(beatmap_descriptor, **selectKw)

    def get_all_downloaded_beatmapsets(self):
        self.cursor.execute("SELECT * FROM  {0[downloaded].table_name} WHERE downloaded=1".format(self.TABLES))
        return self.cursor.fetchall()

    def get_beatmapset_downloaded(self, beatmapset_descriptor: Union[Beatmap,DownloadedBeatmapset,int]):
        if not isinstance(beatmapset_descriptor, int):
            beatmapset_descriptor = beatmapset_descriptor['beatmapset_id']
        self.cursor.execute("SELECT * FROM {0[downloaded].table_name} WHERE beatmapset_id={1}".format(self.TABLES, beatmapset_descriptor))
        return self.cursor.fetchone()
    
    def check_exists_in_downloaded(self, beatmapset_descriptor: Union[Beatmap,DownloadedBeatmapset,int]):
        return self.get_beatmapset_downloaded(beatmapset_descriptor=beatmapset_descriptor) is not None


class CursorTask:
    def __init__(self, target_method:str, args: Tuple, kwargs: Dict):
        self.target_method = target_method
        self.args = args
        self.kwargs = kwargs
    
    def __repr__(self):
        return "<{} object targetMethod={} argsCount={} kwargsCount={}>".format(self.__class__.__name__, self.target_method, self.args.__len__(), self.kwargs.__len__())


class CursorProxy:
    def __init__(self, database:str, cursor: sqlite3.Cursor = None):
        self.database = database
        self.connection: sqlite3.Connection = None
        self.cursor: sqlite3.Cursor = cursor
        self.proxy_connection: sqlite3.Connection = None
        self.proxy_cursor: sqlite3.Cursor = None
        self.daemon: Thread = Thread(target=self.run_queued_task, name='CursorProxy Daemon Thread', daemon=True)
        self.queue: Queue = Queue()
        self._proxy_map = {}
        self._init()
        
        if cursor is not None:
            self.connection = self.cursor.connection
        else:
            self.connection = sqlite3.connect(self.database)
            self.cursor = self.connection.cursor()

    def _init(self):
        self.daemon.start()
    
    def __getattribute__(self, _name: str):
        try:
            return super().__getattribute__(_name)
        except AttributeError:
            return self._proxy_map.get(_name, self.make_proxy(_name))
            # raise AttributeError('\'{}\' is not found in this object.'.format(_name))

    def __call__(self, *args: Any, **kwds: Any):
        return self.cursor.__call__(*args, **kwds)

    def __repr__(self):
        return "<{} object for cursor={}>".format(self.__class__.__name__, self.cursor)

    def run_queued_task(self):
        try:
            self.proxy_connection = sqlite3.connect(self.database)
            self.proxy_cursor = self.proxy_connection.cursor()
            while True:
                task: CursorTask = self.queue.get(True)
                self.proxy_cursor.__getattribute__(task.target_method)(*task.args, **task.kwargs)
        finally:
            self.proxy_cursor.close()
    
    def enqueue_task(self, method_name: str, args: Tuple, kwargs: Dict):
        return self.queue.put(CursorTask(method_name, args, kwargs))

    def make_proxy(self, method_name: str):
        def prxy(*args, **kwargs):
            return self.proxy(method_name, *args, **kwargs)
        return prxy

    def proxy(self, method_name: str, *args, immediate: bool = False, **kwargs):
        if immediate:
            return self.cursor.__getattribute__(method_name)(*args, **kwargs)
        return self.enqueue_task(method_name, args=args, kwargs=kwargs)


class MultiThreadedOsuDB(osuDB):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cursor = self.cursor
        self.cursor: CursorProxy = CursorProxy(self.database, self._cursor)
