with open("cli-help", 'r') as file:
	__doc__ = file.read().strip("\"")
import sys
import subprocess
import asyncio
import requests
import aiohttp
import re
import json
import time
from getopt import getopt
from datetime import datetime
from DBMan import osuDB
from progress_bar import make_progress, make_simple_progress


class Api:
	def __init__(self,
				 apiKey: str = '',
				 osu_credentials: dict = {},
				 debug: bool = False):
		self.apiKey = apiKey

		self.debug = debug

		self.base_url = 'https://osu.ppy.sh'
		self.apiKey_url = 'https://osu.ppy.sh/p/api'
		self.api_url = 'https://osu.ppy.sh/api/'
		self.session_url = f"{self.base_url}/session"
		self.beatmap_url = f"{self.base_url}/beatmapsets/{{0[beatmapset_id]}}"
		self.beatmap_download_url = f"{self.beatmap_url}/download"

		self.beatmap_download_dir = "./downloads"
		self.beatmap_default_filename = "{0[beatmapset_id]} {0[artist]} - {0[title]}"
		self.dump_html = {'get_token': "_token_dump.html"}
		
		try:
			subprocess.check_output(['mkdir', self.beatmap_download_dir], shell=True)
		except subprocess.CalledProcessError:
			pass
		
		self.session = requests.Session()
		self.credentials = osu_credentials
		self.login()

	def get_token(self):
		# access the osu! homepage
		headers = {'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
		self.session.headers = headers
		homepage = self.session.get(self.base_url)

		dump_file = self.dump_html.get("get_token")
		with open(dump_file, 'w', encoding='utf-8') as file:
			file.write(homepage.text)
		# extract the CSRF token sitting in one of the <meta> tags
		regex = re.compile(r".*?csrf-token.*?content=\"(.*?)\">", re.DOTALL)
		match = regex.match(homepage.text)

		try:
			csrf_token = match.group(1)
			return csrf_token
		except AttributeError:
			print("Token Error: 429 Too Many Requests.")

	def login(self):
		data = self.credentials
		data["_token"] = self.get_token()
		headers = {"referer": self.base_url}

		res = self.session.post(self.session_url, data=data, headers=headers)

		if self.debug:
			print(f"|+|Login Process\n"
				  f"   Data        : {data}\n"
				  f"   Headers     : {headers}\n"
				  f"   Status Code : {res.status_code}\n")

		if res.status_code != requests.codes.ok:
			return False
		return True

	def request(self,
				endpoint: str,
				parameters: dict = {}):
		url = self.api_url + endpoint
		parameters.update({'k': self.apiKey})
		respObj = requests.get(url=url, params=parameters)

		if self.debug:
			print(f"|+|Request Process\n"
				  f"   Url         : {url}\n"
				  f"   Params      : {parameters}\n"
				  f"   Status Code : {respObj.status_code}\n")
		return respObj

	async def request_async(self,
							endpoint: str,
							parameters: dict = {}) -> aiohttp.ClientResponse:
		parameters.update({'k': self.apiKey})
		url = self.api_url + endpoint + f"?{'&'.join([f'{k}={v}' for k, v in parameters.items()])}"
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as r:
				if r.status == 200:
					return r

	def download(self, beatmap_info, filename: str = None):
		beatmap_url = self.beatmap_url.format(beatmap_info)
		download_url = self.beatmap_download_url.format(beatmap_info)

		download_dir = self.beatmap_download_dir
		filename = filename if filename is not None else self.beatmap_default_filename
		filename = filename.format(beatmap_info)
		filename = filename if filename.endswith('.osz') else f"{filename}.osz"
		filename = re.sub(r"[/\\:*?<>|\"]", '', filename)

		start = datetime.now().timestamp()

		#resp = self.session.get(download_url, headers={"referer": beatmap_url}, allow_redirects=True)
		with self.session.get(download_url,
							  headers={"referer": beatmap_url},
							  allow_redirects=True,
							  stream=True) as resp:
			chunk_size = 512
			progressBarLength = 20
			content = b''
			progress = 0
			maxProgress = int(resp.headers['Content-Length'])
			startTime = time.time()

			for chunk in resp.iter_content(chunk_size):
				if chunk:
					content += chunk
					progress += len(chunk)
					elapsedTime = time.time()-startTime+1
					prefix = f""
					suffix = f" | {fmtSize(progress)} of {fmtSize(maxProgress)}    {fmtSize(round(progress/elapsedTime,2), suffix='b')}ps ({round(elapsedTime, 2)}s)"
					#print(f"{make_simple_progress(progress, maxProgress, progressBarLength, prefix=prefix, suffix=suffix):<70}", end='')
					print(f"{make_progress(progress, length=progressBarLength, vmax=maxProgress, prefix=prefix, suffix=suffix)}", end=f"{'':<5}")
			print(f"\nDownloaded Beatmap.")


		if self.debug:
			print(f"|+|Download Process\n"
				  f"   Beatmap Info : {beatmap_info}\n"
				  f"   DownloadUrl  : {download_url}\n"
				  f"   BeatmapUrl   : {beatmap_url}\n"
				  f"   FilePath     : {download_dir}\\{filename}\n"
				  f"   Status Code  : {resp.status_code}\n")

		if resp.ok:
			try:
				with open("\\".join([download_dir, filename]), 'wb') as file:
					file.write(content)
			except Exception:
				print(sys.exc_info())
				with open(f"{beatmap_info['beatmapset_id']}.osz", 'wb') as file:
					file.write(content)
			return True
		return self.download(beatmap_info, filename)

	def get_beatmaps(self,
					 parameters: dict = {}):
		endpoint = "get_beatmaps"
		respObj = self.request(endpoint=endpoint, parameters=parameters)
		return respObj

	def get_user(self,
				 parameters: dict = {}):
		endpoint = "get_user"
		respObj = self.request(endpoint=endpoint, parameters=parameters)
		return respObj


def fmtSize(num, suffix='B', decimalPlaces: int = 2):
	num = int(num)
	for unit in ['','K','M','G','T','P','E','Z']:
		if abs(num) < 1024.0:
			return f"{num:.{decimalPlaces}f} {unit}{suffix}"
		num /= 1024.0
	return f"{num:.{decimalPlaces}f} Y{suffix}"


def paramsGetter(KeyPromptPair: dict):
	params = {}
	for key, prompt in KeyPromptPair.items():
		inp = input(prompt)
		params.update({key:inp}) if inp != '' else None
	return params


def loadJson(filename):
	with open(filename, 'r') as file:
		data = json.load(file)
		return data


def convertDateFmt(string, fmt = '%Y-%m-%d'):
	formats = ['%y-%m-%d', '%Y-%m-%d', '%y/%m/%d', '%Y/%m/%d', '%y.%m.%d', '%Y.%m.%d', '%y %m %d', '%Y %m %d',
			   '%d-%m-%y', '%d-%m-%Y', '%d/%m/%y', '%d/%m/%Y', '%d.%m.%y', '%d.%m.%Y', '%d %m %y', '%d %m %Y', '%d%m%y', '%d%m%Y']

	for format in formats:
		try:
			dtObj = datetime.strptime(string, format)
			return dtObj.strftime(fmt)
		except ValueError:
			pass


def removeDuplicate(_list:list, grouping_key = "beatmapset_id", eliminator_key = "beatmap_id"):
	# Parsing Data And Changing The Structure
	data = {}
	for item in _list:
		try:
			data[item[grouping_key]].append(item)
		except KeyError:
			try:
				data[item[grouping_key]] = [item]
			except KeyError:
				continue

	# Processing Data
	return_data = []
	for item in data.values():
		return_data.append(max(item, key= lambda i: i[eliminator_key]))

	return return_data


class Interface:
	def __init__(self, configFile, database='db.sqlite3', debug = False):
		self.configFile = configFile
		self.config = {}
		self.api = None
		self.args = sys.argv
		self.database = database
		self.db = osuDB(database=database)

		self.filterConditions = {}

		self.debug = debug

	def start(self, cli=False):
		self.loadConfig()
		self.configApi()

		self.db.execute(f"""CREATE TABLE IF NOT EXISTS beatmapsets (
		id integer PRIMARY KEY NOT NULL UNIQUE,
		downloaded bool NOT NULL Default False)""")


		if cli:
			return self.cli()
		if len(self.args) > 1:
			return self.cli()
		return self.main()

	def loadConfig(self):
		self.config = loadJson(self.configFile)

	def configApi(self):
		self.api = Api(self.config['api-tokens'].pop('osu'), self.config['osu-credentials'], debug=self.debug)
		if self.debug:
			print(f"|=|Interface.configApi Process\n"
				  f"   Api    : {self.api}\n"
				  f"   Config : {self.config}\n")
		return self.api


	def main(self):

		api = self.api

		while True:
			params = {}
			print("""-------------------
Welcome To OSU API
Please enter your choice.
[u]User
[b]Beatmaps
[d]Download beatmap from list
[x]Exit""")
			choice = input("Choice:")
			if choice.lower() == 'u':
				print("\n--User--\nRequest Parameters:")
				params = paramsGetter({'u': "username:",
									   'm': f"Game Mode [0:Std, 1:Taiko, 2:CtB, 3:Mania | enter for none]:"})
				resp = api.get_user(parameters=params)
				print(resp.json())
				input("Press enter to return.")
				continue
			elif choice.lower() == 'b':
				print("\n--Beatmaps--\nRequest Parameters:")
				params = paramsGetter({'since': f"Since [format: yyyy-mm-dd | enter for none]:",
									   'm': f"Game Mode [0:Std, 1:Taiko, 2:CtB, 3:Mania | enter for none]:",
									   'limit': f"limit [result size limit| enter for default]:"})
				filename = input("Filename:")
				resp = api.get_beatmaps(parameters=params)
				with open(filename, 'w') as f:
					json.dump(resp.json(), f, indent=4)
				input("Press enter to return.")
				continue
			elif choice.lower() == 'd':
				print("\n--Beatmaps Downloader--\nParameters:")
				filename = input("Beatmap List Filename:")
				with open(filename, 'r') as file:
					beatmaps_data = json.load(file)
			elif choice.lower() == 'x':
				exit()

	def filterKey(self, beatmap):
		for condition, key in self.filterConditions.items():
			if not key(beatmap[condition]):
				return False
		return True

	def filterBeatmaps(self, beatmapList, key: callable = None):
		newBeatmapList = []
		for item in beatmapList:
			try:
				if key(item):
					newBeatmapList.append(item)
				# Appends only if the item has all the attributes listed, else continue
			except KeyError:continue
		return newBeatmapList

	def cli(self):
		if len(self.args) > 1:
			command = self.args[1]
			api = self.api

			params = {'since':"", 'm':"", 'limit':""}
			params.clear()



			opts, args = getopt(self.args[2:], 's:m:l:a:q:f:r:dh', ['since=', 'mode=', 'game-mode=', 'limit=',
															   'approved=', 'qualification=', 'diff=', 'difficulty=', 'difficulty-rating=',
															   'favourite=', 'rating=', 'debug', 'help'])

			for opt, value in opts:
				if opt in ['-s', '--since']:
					params.update({'since': convertDateFmt(value)})
				elif opt in ['-m', '--mode', '--game-mode']:
					params.update({'m': value})
				elif opt in ['-l', '--limit']:
					params.update({'limit': value})
				elif opt in ['-a', '-q', '--approved', '--qualification']:
					qualifications = value
					self.filterConditions['approved'] = lambda approved: approved in qualifications
				elif opt in ['--diff', '--difficulty', '--difficulty-rating']:
					try:
						lowerBound, upperBound = sorted([float(rating) for rating in value.split("-")])
					except ValueError:
						lowerBound, upperBound = [float(value) for i in range(2)]
					self.filterConditions['difficultyrating'] = lambda rating: upperBound >= float(rating) >= lowerBound
				elif opt in ['-f', '--favourite']:
					min_fav_count = int(value)
					self.filterConditions['favourite_count'] = lambda fav_count: int(fav_count) >= int(min_fav_count)
				elif opt in ['-r', '--rating']:
					min_rating = float(value)
					self.filterConditions['rating'] = lambda rating: float(rating) >= float(min_rating)
				elif opt in ['-d', '--debug']:
					self.debug = True
				elif opt in ['-h', '--help']:
					print(__doc__)
					exit()

			if self.debug:
				print(f"|>|Interface.Cli Process\n"
					  f"   Command           : {command}\n"
					  f"   Opts              : {opts}\n"
					  f"   Args              : {args}\n"
					  f"   Parameters        : {params}\n"
					  f"   Filter Conditions : {self.filterConditions}")

			if command.lower() in ['help', 'h']:
				print(__doc__)
				exit()
			elif command.lower() in ['d', 'download']:
				resp = api.get_beatmaps(parameters=params)
				beatmapList = resp.json()
				cleaned = lambda: removeDuplicate(beatmapList)
				print(f"Found {len(beatmapList)} Beatmaps and {len(cleaned())} Beatmapsets.")
				beatmapList = self.filterBeatmaps(beatmapList, key=self.filterKey)
				print(f"Filtered: {len(beatmapList)} Beatmaps and {len(cleaned())} Beatmapsets.")
				print("Starting Download...\n")


				for idx, beatmap in enumerate(beatmapList):
					print(f"Beatmap #{idx+1}")
					self.db.execute(f"SELECT * FROM beatmapsets WHERE ID={beatmap['beatmapset_id']}")
					record = self.db.cursor.fetchall()
					if self.debug:
						print(f"   Records in database : {record}\n"
							  f"   Beatmapset_id : {beatmap['beatmapset_id']}")
					print("Processing Beatmap: {0[beatmapset_id]} {0[artist]} - {0[title]}".format(beatmap))
					if len(record) > 0:
						print("Already Downloaded In Database.\n")
					if len(record) == 0:
						print("Downloading Beatmap...")
						api.download(beatmap_info=beatmap)
						self.db.execute("INSERT OR IGNORE INTO beatmapsets VALUES (?,?)", (beatmap['beatmapset_id'], True))
						print("Beatmap Downloaded.\n")

					self.db.commit()

				print("Finished Downloading.")




if __name__ == '__main__':
	import pprint

	if '-d' in sys.argv or '--debug' in sys.argv:
		interface = Interface("config.json", debug=True)
	else:
		interface = Interface("config.json", debug=False)
	interface.loadConfig()
	interface.start()