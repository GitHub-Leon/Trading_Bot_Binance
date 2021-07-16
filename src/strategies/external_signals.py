# used for directory handling
import glob
import os

from src.classes.TxColor import txcolors
from src.config import DEBUG, SIGNALS_FOLDER, lock
from src.helpers.scripts.logger import debug_log


def external_buy_signals():
    external_buy_list = {}
    signals = {}

    # check directory and load pairs from files into external_list
    with lock:
        debug_log("Check directory and load pairs from files into external_buy_list", False)
    signals = glob.glob(SIGNALS_FOLDER + "/buy_*.exs")
    for filename in signals:
        for line in open(filename):
            symbol = line.strip()
            external_buy_list[symbol] = symbol
        try:
            os.remove(filename)
            with lock:
                debug_log(f"Removed file {filename}", False)
        except:
            with lock:
                debug_log(f'Could not remove external signalling file', True)
                if DEBUG:
                    print(f'{txcolors.WARNING}Could not remove external signalling file{txcolors.DEFAULT}')

    return external_buy_list


def external_sell_signals():
    external_sell_list = {}
    signals = {}

    # check directory and load pairs from files into external_list
    with lock:
        debug_log("Check directory and load pairs from files into external_sell_list", False)
    signals = glob.glob(SIGNALS_FOLDER + "/sell_*.exs")
    for filename in signals:
        for line in open(filename):
            symbol = line.strip()
            external_sell_list[symbol] = symbol
        try:
            os.remove(filename)
            with lock:
                debug_log(f"Removed file {filename}", False)
        except:
            with lock:
                debug_log(f'Could not remove external signalling file {filename} SELL', True)
                if DEBUG:
                    print(f'{txcolors.WARNING}Could not remove external signalling file{txcolors.DEFAULT}')

    return external_sell_list
