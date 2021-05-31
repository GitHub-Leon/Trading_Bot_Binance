# used for directory handling
import glob
import os

from src.classes.TxColor import txcolors
from src.config import DEBUG, SIGNALS_FOLDER


def external_signals():
    external_list = {}
    signals = {}

    # check directory and load pairs from files into external_list
    signals = glob.glob(SIGNALS_FOLDER + "/*.exs")
    for filename in signals:
        for line in open(filename):
            symbol = line.strip()
            external_list[symbol] = symbol
        try:
            os.remove(filename)
        except:
            if DEBUG:
                print(f'{txcolors.WARNING}Could not remove external signalling file{txcolors.DEFAULT}')

    return external_list
