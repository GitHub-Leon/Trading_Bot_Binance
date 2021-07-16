import sys

from src.classes.StampedOut import StampedOut
from src.helpers.scripts.logger import debug_log, LOCK_CONSOLE


def console_input():
    sys.stdout = StampedOut()  # timestamp

    debug_log("Enter input", False)
    with LOCK_CONSOLE:
        cmd = input("--> ")

    return cmd
