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
    "api-key": {
        "osu": "A Hexadecimal String Representing Your API KEY"
    },
    "credentials": {
        "osu": {
            "username": "Your username",
            "password": "Your password"
        }
    }
}
```
>**For more detail, you can consider visiting these: [Config Sample](./config.sample.json) and [Config Schematics](./config.scematics.json).**

Now you can insert the token you got from osu.ppy.sh/p/api into the `api-key > osu` field and insert your username and password into `credentials > osu > username` and `credentials > osu > password` respectively.

## USAGE
After configuring the project, You could finally start using it!
The beatmap downloader can be used in CLI and Interactive mode.
it will start in CLI mode **if** the interface detects argument, else it will start in Interactive mode.


### CLI
Example:
```bash
> python main.py Download -s 2021-06-26 
.. #Downloads all beatmapsets since 2021 June 26 (limit 500)
```
Or you can use my preset (you can change the preset itself too) by: 
```bash
> python preset.py 
.. # Downloads as per preset
```
**NOTE: PRESET IS NOT YET AVAILABLE IN THIS BRANCH**

### CLI Commands & Options
```bash
> python main.py --help
usage: main.py [-h] [--download-directory DIRECTORY]
               [--download-chunk-size CHUNK_SIZE] [--record-beatmaps]
               [--lookup-in-database] [-d] [-s DATETIME] [-m MODE] [-l LIMIT]
               [-nv] [-a QUALIFICATION] [--diff RATING] [-f FAVOURITE_COUNT]
               [-r RATING]
               [ACTION]

This is the cli interface for osu-map-downloader.

positional arguments:
  ACTION                Action to do.

options:
  -h, --help            show this help message and exit

Configurations:
  --download-directory DIRECTORY
                        Sets download directory for api. Default='./Downloads'
  --download-chunk-size CHUNK_SIZE
                        Sets download chunk size for api. Default=512b
  --record-beatmaps     Whether to save beatmaps to database or not.
  --lookup-in-database  Whether to search for beatmaps to download from
                        accumulated database.
  -d, --debug           Sets debug in printer. Default=False

Get Beatmaps Params:
  -s DATETIME, --since DATETIME
                        Add get beatmaps param since given date. Supported
                        formats: YYYY-MM-DD, YYYY/MM/DD, DD-MM-YY, DD/MM/YY
  -m MODE, --mode MODE, --game-mode MODE
                        Add get beatmaps param for game mode. Modes: 0 = osu!,
                        1 = Taiko, 2 = CtB, 3 = osu!mania
  -l LIMIT, --limit LIMIT
                        Adds limit to return beatmaps count. Default=500

Download Params:
  -nv, --no-video       Whether to download beatmapset with video or not.

Download Filters:
  -a QUALIFICATION, -q QUALIFICATION, --approved QUALIFICATION, --qualification QUALIFICATION
                        Adds beatmaps filter to specified approved. To add
                        multiple qualifications, stack it like: '-q 0 -q 1
                        ...'. Qualifications: 4 = loved, 3 = qualified, 2 =
                        approved, 1 = ranked, 0 = pending, -1 = WIP, -2 =
                        graveyard
  --diff RATING, --difficulty RATING, --difficulty-rating RATING
                        Adds beatmaps filter for range or exact match on
                        difficultyrating. Ratings will be converted to floats.
                        Rating formats: [x.xx] or [x] and [x.xx-y.yy]
  -f FAVOURITE_COUNT, --favourite FAVOURITE_COUNT
                        Adds beatmaps filter for minimum favourite count on
                        the beatmapset.
  -r RATING, --rating RATING
                        Adds beatmaps filter for minimum rating on the
                        beatmapset.

```

## Development
Please note that some functionality is not available yet as of now in this rewrite branch.
This branch is essentially a rewrite compared to the main branch, as such the project has became a lot more robust. This project can now facilitate a lot more possible addons while staying organized.

---
Thanks for reading.