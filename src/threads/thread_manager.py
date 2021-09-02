import glob
import importlib
import os
# used to create threads & dynamic loading of modules
import threading
import time

from enum import Enum
from src.classes.TxColor import txcolors
from src.config import SIGNALLING_MODULES, DEBUG, SIGNALS_FOLDER, TRADING_VIEW_FOLDER, MSG_DISCORD, PAY_FEE_WITH_BNB
from src.helpers.scripts.logger import debug_log, console_log


class Path(Enum):
    OPTIONAL = 'src.threads.optional_threads'
    STRATEGY = 'src.threads.strategy_threads'
    DEFAULT = 'src.threads.default_threads'


def load_all_threads():
    """Load all threads"""
    load_optional_threads()
    load_signal_threads()


def load_optional_threads():
    # Start Discord msg thread
    if MSG_DISCORD:
        debug_log(f'Starting discord_msg_balance_thread', False)
        if DEBUG:
            console_log(f'Starting discord_msg_balance_thread')

        module = 'discord_msg_balance_thread'
        start_thread(module, Path.OPTIONAL)

    # Start BNB auto buy thread
    if PAY_FEE_WITH_BNB:
        start_bnb_auto_buy_thread()


def load_signal_threads():
    """Load threads for signalling modules (referenced in config file)"""
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

    # load signalling modules
    debug_log("Load signalling modules", False)
    try:
        if SIGNALLING_MODULES is not None:
            # Start pause bot thread
            if 'pausebot_standard' in SIGNALLING_MODULES:
                debug_log(f'Starting pausebot', False)
                if DEBUG:
                    console_log(f'Starting pausebot')

                module = 'pause_bot'
                start_thread(module, Path.STRATEGY)

            # Start trading_view threads
            if len(SIGNALLING_MODULES) > 0:
                for module in SIGNALLING_MODULES:
                    if DEBUG:
                        debug_log(f'Starting {module}', False)
                        console_log(f'Starting {module}')
                    start_thread(module, Path.STRATEGY)
        else:
            debug_log(f'No modules to load', False)

    except Exception as e:
        debug_log("Error while loading modules. Error-Message: " + str(e), True)


def start_bnb_auto_buy_thread():
    debug_log(f'Starting bnb_auto_buy_thread', False)
    if DEBUG:
        console_log(f'Starting bnb_auto_buy_thread')

    module = 'discord_msg_balance_thread'
    start_thread(module, Path.OPTIONAL)


def start_thread(module, path):
    my_module = {module: importlib.import_module('.' + module, path)}

    debug_log("Threading the modules", False)

    t = threading.Thread(target=my_module[module].do_work, args=())
    t.daemon = True
    t.start()
    time.sleep(2)
