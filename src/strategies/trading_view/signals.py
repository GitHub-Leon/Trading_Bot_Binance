import glob
import importlib
import os
# used to create threads & dynamic loading of modules
import threading
import time

from src.classes.TxColor import txcolors
from src.config import SIGNALLING_MODULES, DEBUG, SIGNALS_FOLDER, TRADING_VIEW_FOLDER
from src.helpers.scripts.logger import debug_log, console_log


def load_signals():
    debug_log("Load signals", False)
    signals = glob.glob(SIGNALS_FOLDER + "/*.exs")

    for filename in signals:
        try:
            os.remove(filename)
        except:
            debug_log("Could not remove external signalling file", True)
            if DEBUG:
                console_log(f'{txcolors.WARNING}Could not remove external signalling file {filename}{txcolors.DEFAULT}')

    if os.path.isfile(SIGNALS_FOLDER + "/paused.exc"):
        try:
            os.remove(SIGNALS_FOLDER + "/paused.exc")
        except:
            debug_log("Could not remove external signalling file", True)
            if DEBUG:
                console_log(f'{txcolors.WARNING}Could not remove external signalling file paused.exc{txcolors.DEFAULT}')

    my_module = {}

    # load signalling modules
    debug_log("Load signalling modules", False)
    try:
        debug_log(f'Starting pausebot', False)
        if DEBUG:
            console_log(f'Starting pausebot')

        module = 'pause_bot'
        my_module[module] = importlib.import_module('.' + module, 'src.helpers.scripts')

        debug_log("Threading the modules", False)

        t = threading.Thread(target=my_module[module].pause_bot, args=())
        t.daemon = True
        t.start()
        time.sleep(2)

        if len(SIGNALLING_MODULES) > 0:
            for module in SIGNALLING_MODULES:
                if DEBUG:
                    debug_log(f'Starting {module}', False)
                    console_log(f'Starting {module}')
                my_module[module] = importlib.import_module('.' + module, TRADING_VIEW_FOLDER)

                debug_log("Threading the modules", False)

                t = threading.Thread(target=my_module[module].do_work, args=())
                t.daemon = True
                t.start()
                time.sleep(2)
        else:
            debug_log(f'No modules to load {SIGNALLING_MODULES}', False)
            console_log(f'No modules to load {SIGNALLING_MODULES}')
    except Exception as e:
        debug_log("Error while loading modules. Error-Message: " + str(e), True)
