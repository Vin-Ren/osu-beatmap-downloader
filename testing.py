import math
import requests
from osu_api import Interface
import osu_api
from threading import Thread


interface = Interface("config.json", debug=True)


def st():
	interface.loadConfig()
	interface.configApi()


def fmtSize(num, suffix='B', decimalPlaces: int = 2):
	num = int(num)
	for unit in ['','K','M','G','T','P','E','Z']:
		if abs(num) < 1024.0:
			return f"{num:.{decimalPlaces}f} {unit}{suffix}"
		num /= 1024.0
	return f"{num:.{decimalPlaces}f} Y{suffix}"


def downloadStream(session, url, chunk_size=4096):

	with session.get(url, headers={"referer": url}, allow_redirects=True, stream=True) as resp:
		resp: requests.Response
		resp_content = b''
		progsize = 0

		for chunk in resp.iter_content(chunk_size):
			if chunk:
				resp_content += chunk
				progsize += len(chunk)
				print_progress(progsize, int(resp.headers['Content-Length']), 50)
				#print(f"\rDownloaded {fmtSize(progsize)} of {fmtSize(resp.headers['Content-Length'])}{'':<10}", end='')
		print(f"\rDownloaded {fmtSize(progsize)} of {fmtSize(resp.headers['Content-Length'])}{'':<10}")
		print(progsize, resp.headers['Content-Length'], progsize-int(resp.headers['Content-Length']))
		return resp, resp_content


def print_progress(curr: int, total: int, max_msg_length: int = 80):
	# [12345678901234567890]
	# [████████------------]
	animBarLen = 20

	if total > 0:
		complete = int((curr * animBarLen) / total)
		remainder = (((curr * animBarLen) % total) / total)
		use_half_block = (remainder <= 0.5) and remainder > 0.1
		if use_half_block:
			with_half_block = f"{'█' * (complete - 1)}▌"
			msg = f"\r[{with_half_block:{animBarLen}}] {fmtSize(curr)} of {fmtSize(total)}"
		else:
			msg = f"\r[{'█' * complete:{animBarLen}}] {fmtSize(curr)} of {fmtSize(total)}"

	else:
		# indeterminite
		pos = curr % (animBarLen + 3)  # 3 corresponds to the length of the '███' below
		anim = '.' * animBarLen + '███' + '.' * animBarLen
		# Use nested replacement field to specify the precision value. This limits the maximum print
		# length of the progress bar. As pos changes, the starting print position of the anim string
		# also changes, thus producing the scrolling effect.
		msg = f'\r[{anim[animBarLen + 3 - pos:]:.{animBarLen}}] {fmtSize(curr)}'

	curr_msg_length = len(msg)
	print(msg.ljust(max_msg_length, " "), end='')

	return curr_msg_length if curr_msg_length > max_msg_length else max_msg_length


st()

