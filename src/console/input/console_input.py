import sys

from src.classes.StampedOut import StampedOut
from src.helpers.scripts.logger import debug_log, LOCK_CONSOLE
from src.console.output.exit import init_exit


def console_input():
    sys.stdout = StampedOut()  # timestamp

    debug_log("Enter input", False)
    try:
        with LOCK_CONSOLE:
            cmd = input("--> ")
    except KeyboardInterrupt:
        init_exit()

    return cmd
