import argparse

import yaml

from src.helpers.scripts.logger import debug_log, console_log

DEFAULT_SETTINGS_FILE = 'settings.json'


def load_config(file, important):
    debug_log(f'Trying to load config file {file}', False)

    try:
        with open(file) as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    except OSError as e:
        debug_log(f'Error while loading config file {file}', True)
        if important:
            console_log(f'No config file {file}')
            exit()
    return False


def write_config(file, content):
    debug_log(f'Write config file {file}', False)

    try:
        with open(file, 'w') as file:
            yaml.dump(content, file)
    except OSError as e:
        debug_log(f'Error while writing config file {file}', True)
    return False


def parse_args():
    debug_log("Trying to parse arguments of config file", False)
    x = argparse.ArgumentParser()
    x.add_argument('--debug', '-d', help="extra logging", action='store_true')
    x.add_argument('--config', '-c', help="Path to config.yml")
    x.add_argument('--creds', '-u', help="Path to creds file")
    return x.parse_args()
