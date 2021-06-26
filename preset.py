from sys import argv
from datetime import datetime
import osu_api
from osu_api import Interface



def getDay(offset=86400):
	dt = datetime.now()
	dt = datetime.fromtimestamp(dt.timestamp() + offset)
	return dt.strftime("%Y-%m-%d")


interface = Interface(configFile="config.json", database="db.sqlite3")


if __name__ == '__main__':
	from getopt import getopt

	days = 2

	opts, args = getopt(argv[1:], 'r:d', ['from-day=', 'debug'])

	for opt, val in opts:
		if opt in ['-r', '--from-day']:
			days = int(val) if int(val) > 0 else int(val*-1)
			argv.remove(opt)
			argv.remove(val)
		if opt in ['-d', '--debug']:
			interface.debug = True

	curDay = osu_api.convertDateFmt(getDay(offset=(-86400*days)))
	interface.args = f"{__name__} Download -s {curDay} -m 0 -q 14 --diff 3.5-10 -f 10".split() + argv[1:]
	interface.start()
