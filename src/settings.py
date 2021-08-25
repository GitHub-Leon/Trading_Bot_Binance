import os

from src.config import DEFAULT_CONFIG_FILE, DEFAULT_CREDS_FILE
from src.helpers.scripts.logger import debug_log


def settings():
    debug_log("Open config file for user", False)
    try:
        os.system("start " + DEFAULT_CONFIG_FILE)
    except Exception as e:
        debug_log("Open config file failed. Error-Message: " + str(e), True)


def creds():
    debug_log("Open cred file for user", False)
    try:
        os.system("start " + DEFAULT_CREDS_FILE)
    except Exception as e:
        debug_log("Open cred file failed. Error-Message: " + str(e), True)
