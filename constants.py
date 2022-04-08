

BASE_URL = "https://osu.ppy.sh"
API_URL = BASE_URL+"/api"

TEMPORARY_FILE_SUFFIX = ".beatmaptmp"
BEATMAPSET_EXTENSION = '.osz'


class Url:
    home = BASE_URL
    session = "%s/session" % BASE_URL
    formattable_beatmapset = "%s/beatmapsets/{0[beatmapset_id]}" % BASE_URL
    formattable_beatmapset_download = "%s/download" % formattable_beatmapset


class Endpoint:
    get_beatmaps = "%s/get_beatmaps" % API_URL
    get_user = "%s/get_user" % API_URL
