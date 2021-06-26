# OSU Beatmap Downloader
A Beatmap Downloader For OSU

## SETUP
### Get API Key
**How to get OSU API Key:**
1. Navigate to osu.ppy.sh/p/api or go to [OSU API docs](https://github.com/ppy/osu-api/wiki) if the former link doesn't work.
2. Enter Application name & Application url
3. Submit the form, after that, you should be able to see an API Key, Copy it and paste it into the config file.

### Install Dependencies
Installing dependencies is simple enough:
```bash
> pip install -r requirements.txt
```
That should install the required dependencies.
>You should change `pip` to `pip3` if it doesn't work.

### Making Configuration File
After you cloned this repository, you should have a file named config.json inside the repo folder.
it's content should be like:
```json
{
    "api-tokens": {
        "osu": "Get Your OSU API KEY from 'https://osu.ppy.sh/p/api'"
    },
    "osu-credentials": {
        "username": "username",
        "password": "password"
    }
}
```
Now you can insert the token you got from osu.ppy.sh/p/api into the `api-tokens > osu` field and insert your username and password into `osu-credentials > username` and `osu-credentials > password` respectively.

## USAGE
After configuring the project, You could finally start using it!
The beatmap downloader can be used in CLI and Interactive mode.
it will start in CLI mode **if** the interface detects argument, else it will start in Interactive mode.

### CLI
Example:
```bash
> python osu_api.py Download -s 2021-06-26 
.. #Downloads all beatmapsets since 2021 June 26 (limit 500)
```
Or you can use my preset (you can change the preset itself too) by:
```bash
> python preset.py 
.. # Downloads as per preset
```

### CLI Commands & Options
```
USAGE: python osu_api.py <Command> [Parameters]

--Commands--
Help		|| Shows this message.
D|Download	|| download beatmaps


--Options--
-s|--since <date>                                 || Pass since parameter to get_beatmaps
                                                  || Date formats: YYYY-MM-DD, YYYY/MM/DD, DD-MM-YY, DD/MM/YY
-m|--mode|--game-mode <gamemode>                  || Pass m parameter to get_beatmaps
                                                  || Gamemode: 0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania
-l|--limit <beatmap count limit default=500>	  || Pass limit parameter to get_beatmaps
-a|-q|--approved|--qualification <qualification>  || Added beatmap filter for approved.
                                                  || Qualifications: 4 = loved, 3 = qualified, 2 = approved, 1 = ranked, 0 = pending, -1 = WIP, -2 = graveyard
                                                  || Qualifications can be stacked, example: "-a 41" would filter for loved & approved maps only.
--diff|--difficulty|--difficulty-rating <rating>  || Added beatmap filter for difficultyrating. Rating will be converted to float.
                                                  || Rating formats: [x.xx] or [x] and [x.xx-y.yy]
                                                  || If given one rating, will only download beatmapset which has a diff rating x or x.xx
                                                  || If given a range[x.xx-y.yy], will only download beatmapset which hass a diff rating inside the range.
-f|--favourite <favourite_count>                  || Added beatmap filter for favourite_count.
                                                  || Will only download beatmapsets with favourite_count higher than the given favourite_count.
-r|--rating <rating>                              || Added beatmap filter for rating.
                                                  || Only download beatmapsets with rating above the given rating.
-d|--debug                                        || Enable Debug
-h|--help                                         || Shows this message
```
## Development
The code isn't really that organized, Its split into 2 files: 
 - [osu_api.py](./osu_api.py)
 -  [DBMan.py](./DBMan.py)

[DBMan.py](./DBMan.py) is just a database manager, really.
Most of the code is in [osu_api.py](./osu_api.py) it contains: `Api`, `Interface`, and utilities.
You can see the code by yourself to see how it works.

---
Thanks for reading.