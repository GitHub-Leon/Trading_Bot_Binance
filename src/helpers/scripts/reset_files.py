import os

from src.helpers.scripts.logger import debug_log


def reset_files():
    debug_log("Trying to reset files", False)
    try:
        # resets trades file after every startup
        if os.path.exists('log/trades.log'):
            os.remove('log/trades.log')
    except Exception as e:
        debug_log("Error in reset_files.py " + str(e), True)
