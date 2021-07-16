import sys

# local dependencies
from src.helpers.scripts.logger import debug_log, console_log
from src.classes.StampedOut import StampedOut


def console_input():
    sys.stdout = StampedOut()  # timestamp

    debug_log("Enter input", False)
    cmd = input("--> ")

    return cmd
