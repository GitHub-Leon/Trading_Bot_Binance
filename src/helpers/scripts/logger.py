import os
from datetime import datetime

# local dependencies
from src.config_log import TRADE_LOG_FILE, INPUT_LOG_FILE, DEBUG_LOG_FILE


if not os.path.exists('log'):  # only create folder, if it does not exist already
    os.mkdir('log')


def trade_log(logline):
    try:
        timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
        with open(TRADE_LOG_FILE, 'a+') as f:
            f.write(f'{timestamp} {logline}\n')
    except:
        return False
    return True


def input_log(logline, is_valid):
    try:
        timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
        with open(INPUT_LOG_FILE, 'a+') as f:
            f.write(f'{timestamp} {"[V]" if is_valid else "[E]"} {logline}\n')
    except:
        return False
    return True


def debug_log(logline, is_error):
    try:
        timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
        with open(DEBUG_LOG_FILE, 'a+') as f:
            f.write(f'{timestamp} {"[I]" if not is_error else "[E]"} {logline}\n')
    except:
        return False
    return True


debug_log("------------------------- START -------------------------", False)
