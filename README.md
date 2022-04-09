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
Can be viewed with:
```bash
> python main.py --help
```

## Development
Please note that some functionality is not available yet as of now in this rewrite branch.
This branch is essentially a rewrite compared to the main branch, as such the project has became a lot more robust. This project can now facilitate a lot more possible addons while staying organized.

---
Thanks for reading.