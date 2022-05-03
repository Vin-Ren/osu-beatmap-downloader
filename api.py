import os
import time
import io

import requests

from utils import *
from WrappedObjects import Config, Credential, Beatmap, User
from constants import BASE_URL, TEMPORARY_FILE_SUFFIX, BEATMAPSET_EXTENSION, Url, Endpoint


printer = PrettyPrinter._get_default()


class osuAPI:
    def __init__(self, api_key: str, credentials: Credential, config: Config, *, initialize=True):
        self.api_key = api_key
        self.credentials = credentials

        self.config = config
        
        self._cached_last_resp = {'get_csrf_token': None, 'login': None, 'request': None}
        self.session = requests.Session()
        self.session.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}
        self._logged_in = False
        
        if initialize:
            self._init()
    
    def _init(self):
        try:
            os.makedirs(self.config.download_dir)
        except FileExistsError:
            pass
        
        self._logged_in = self.login()
        
    @property
    def headers(self):
        return self.session.headers
    
    @headers.setter
    def headers(self, replacement: dict):
        self.session.headers = replacement
    
    def __repr__(self):
        return "<osuAPI LoggedIn={} Username={}>".format(self._logged_in, self.credentials.username)
    
    def get_csrf_token(self):
        resp = self.session.get(Url.home)
        self._cached_last_resp['get_csrf_token'] = resp
        if resp.status_code == 200:
            homepage_content = resp.text
            match = CSRF_TOKEN_REGEX.match(homepage_content)
            try:
                return match.group(1)
            except AttributeError:
                print("CSRF Token Error: Could not find CSRF token in the page.")
        elif resp.status_code == 429:
            print("CSRF Token Error: 429 Too Many Requests.")
    
    def login(self):
        data = dict(self.credentials)
        data['_token'] = self.get_csrf_token()
        headers = {'referer': Url.home}
        
        resp = self.session.post(Url.session, data=data, headers=headers)
        self._cached_last_resp['login'] = resp
        
        printer.print_debug('Login Process', 
                            {'Data': data, 'Headers': headers, 'Status Code': resp.status_code})
        return resp.ok
    
    def request(self, url: str, *, params: dict = {}, **kw):
        url = url if url.startswith(BASE_URL) else BASE_URL+(url if url.startswith('/') else '/{}'.format(url))
        params.update({'k': self.api_key})
        
        resp = self.session.get(url=url, params=params, **kw)
        self._cached_last_resp['request'] = resp
        
        printer.print_debug('Request Process', 
                            {'Url':url, 'Params': params, 'Status Code': resp.status_code})
        return resp
    
    def download(self, beatmap: Beatmap, pipe_handler: io.BytesIO, params={}, retry=False):
        beatmapset_url = Url.formattable_beatmapset.format(beatmap)
        beatmapset_download_url = Url.formattable_beatmapset_download.format(beatmap)
        
        headers = {'referer': beatmapset_url}
        
        with self.session.get(url=beatmapset_download_url, params=params, headers=headers, allow_redirects=True, stream=True) as download_stream:
            start_time = time.time()
            # progress = 0
            max_progress = int(download_stream.headers['Content-Length'])
            
            for chunk in download_stream.iter_content(self.config.download_chunk_size):
                if not chunk:
                    break
                pipe_handler.write(chunk)
                elapsed_time = time.time()-start_time+0.001 # +1ms, prevent div by 0 error
                suffix = " | {curr} of {max}    {speed} ({elapsed_time}s)"
                suffix = suffix.format(curr=metric_size_formatter(pipe_handler.tell()), max=metric_size_formatter(max_progress), 
                                       speed=metric_size_formatter(round(pipe_handler.tell()/elapsed_time, 2), suffix='bps'), elapsed_time=round(elapsed_time,2))
                print(make_progress_bar(pipe_handler.tell(), length=self.config.download_progress_bar_length, vmax=max_progress, suffix=suffix), end=' '*5)
            print('\nDownloaded Beatmap.')
        
        printer.print_debug('Download Process', 
                            {'Beatmap Info':beatmap, 'Download Url':beatmapset_download_url, 'Beatmapset Url': beatmapset_url, 
                             'Target File Stream': repr(pipe_handler), 'Params': params, 'Status Code': download_stream.status_code})
        if download_stream.ok:
            return True
        if retry:
            return self.download(beatmap, pipe_handler, retry)

    def download_to_file(self, beatmap: Beatmap, filename: str = None, params={}):
        filename = (filename or self.config.formattable_beatmap_filename).format(beatmap)
        filename = filename if filename.endswith(BEATMAPSET_EXTENSION) else filename+BEATMAPSET_EXTENSION
        filename = remove_illegal_name_characters(filename)
        
        filepath = os.path.join(self.config.download_dir, filename)
        
        success = False
        with open(filepath+TEMPORARY_FILE_SUFFIX, 'wb') as file_handler:
            success = self.download(beatmap, file_handler, params=params)
            file_handler.flush()
        if success:
            try:
                os.rename(filepath+TEMPORARY_FILE_SUFFIX, filepath)
            except FileExistsError:
                os.replace(filepath+TEMPORARY_FILE_SUFFIX, filepath)
                pass
    
    def get_beatmaps(self, params: dict):
        resp = self.request(url=Endpoint.get_beatmaps, params=params)
        if resp.ok:
            return [Beatmap(entry) for entry in resp.json()]
    
    def get_users(self, params: dict):
        resp = self.request(url=Endpoint.get_user, params=params)
        if resp.ok:
            return [User(entry) for entry in resp.json()]
