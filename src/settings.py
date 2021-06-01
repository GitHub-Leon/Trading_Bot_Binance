import os

# Local Dependencies
from src.config import DEFAULT_CONFIG_FILE
from src.helpers.scripts.logger import debug_log


def settings():
    debug_log("Open config file for user", False)
    try:
        os.system("start " + DEFAULT_CONFIG_FILE)
    except Exception as e:
        debug_log("Open config file failed. Error-Message: " + str(e), True)
