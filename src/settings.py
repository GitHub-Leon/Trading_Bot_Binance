import os

# local dependencies
from src.config import DEFAULT_CONFIG_FILE, lock
from src.helpers.scripts.logger import debug_log


def settings():
    with lock:
        debug_log("Open config file for user", False)
    try:
        os.system("start " + DEFAULT_CONFIG_FILE)
    except Exception as e:
        with lock:
            debug_log("Open config file failed. Error-Message: " + str(e), True)
