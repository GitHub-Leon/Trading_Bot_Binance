import glob
import importlib
import os
# used to create threads & dynamic loading of modules
import threading
import time

from src.classes.colors import txcolors
# local dependencies
from src.config import SIGNALLING_MODULES, DEBUG, SIGNALS_FOLDER, TRADING_VIEW_FOLDER
from src.helpers.scripts.logger import debug_log


def load_signals():
    debug_log("Load signals", False)
    signals = glob.glob(SIGNALS_FOLDER + "/*.exs")

    try:
        for filename in signals:
            for line in open(filename):
                try:
                    os.remove(filename)
                except:
                    debug_log("Could not remove external signalling file", True)
                    if DEBUG:
                        print(f'{txcolors.WARNING}Could not remove external signalling file {filename}{txcolors.DEFAULT}')

        if os.path.isfile(SIGNALS_FOLDER + "/paused.exc"):
            try:
                os.remove(SIGNALS_FOLDER + "/paused.exc")
            except:
                debug_log("Could not remove external signalling file", True)
                if DEBUG:
                    print(f'{txcolors.WARNING}Could not remove external signalling file {filename}{txcolors.DEFAULT}')
    except Exception as e:
        debug_log("Error while reading and deleting signal files. Error-Message: " + str(e), True)

    my_module = {}

    # load signalling modules
    debug_log("Load signalling modules", False)
    try:
        if len(SIGNALLING_MODULES) > 0:
            for module in SIGNALLING_MODULES:
                if DEBUG:
                    debug_log(f'Starting {module}', False)
                    print(f'Starting {module}')
                my_module[module] = importlib.import_module('.' + module, TRADING_VIEW_FOLDER)
                debug_log("Treading the modules", False)
                t = threading.Thread(target=my_module[module].do_work, args=())
                t.daemon = True
                t.start()
                time.sleep(2)
        else:
            debug_log(f'No modules to load {SIGNALLING_MODULES}', False)
            print(f'No modules to load {SIGNALLING_MODULES}')
    except Exception as e:
        debug_log("Error while loading modules. Error-Message: " + str(e), True)
