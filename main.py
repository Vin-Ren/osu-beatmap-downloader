from WrappedObjects import Credential
from utils import load_json

from interface import Interface


if __name__ == '__main__':
    from config import config
    json_config = load_json(config.json_config)
    interface = Interface(config, json_config['api-key']['osu'], Credential(json_config["credentials"]["osu"]))
    interface.start()
