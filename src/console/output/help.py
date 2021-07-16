# local dependencies
from src.helpers.scripts.logger import debug_log
from src.config import lock


def helps():
    with lock:
        debug_log("User asked for help", False)
        print("need help?")
