# used for directory handling
import glob
import os

from src.classes.colors import txcolors
from src.config import DEBUG, SIGNALS_FOLDER
from src.helpers.scripts.logger import debug_log


def external_signals():
    external_list = {}
    signals = {}

    # check directory and load pairs from files into external_list
    debug_log("Check directory and load pairs from files into external_list", False)
    signals = glob.glob(SIGNALS_FOLDER + "/*.exs")
    for filename in signals:
        for line in open(filename):
            symbol = line.strip()
            external_list[symbol] = symbol
        try:
            os.remove(filename)
            debug_log("removed file", False)
        except:
            debug_log(f'Could not remove external signalling file', True)
            if DEBUG:
                print(f'{txcolors.WARNING}Could not remove external signalling file{txcolors.DEFAULT}')

    return external_list
