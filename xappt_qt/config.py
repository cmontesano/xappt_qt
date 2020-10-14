import os
from configparser import ConfigParser

from xappt_qt.constants import APP_CONFIG_FILE, APP_CONFIG_PATH


def default_config() -> ConfigParser:
    config = ConfigParser()
    config['browser'] = {
        'launch-new-process': 'true',
    }
    return config


def read_config() -> ConfigParser:
    config = default_config()
    config.read(APP_CONFIG_FILE)
    return config


def write_config(config: ConfigParser):
    os.makedirs(APP_CONFIG_PATH, exist_ok=True)
    with open(APP_CONFIG_FILE, "w") as fp:
        config.write(fp, space_around_delimiters=False)
