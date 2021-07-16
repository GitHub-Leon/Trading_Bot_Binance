import sys

# local dependencies
from src.helpers.scripts.logger import debug_log
from src.classes.StampedOut import StampedOut
from src.config import lock


def console_input():
    sys.stdout = StampedOut()  # timestamp

    with lock:
        debug_log("Enter input", False)
    return input("--> ")
