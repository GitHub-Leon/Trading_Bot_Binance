import sys

from src.classes.StampedOut import StampedOut
from src.helpers.scripts.logger import debug_log


def console_input():
    sys.stdout = StampedOut()  # timestamp

    debug_log("Enter input", False)
    cmd = input("--> ")

    return cmd
