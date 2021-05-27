import time
import glob
import os

# used to create threads & dynamic loading of modules
import threading
import importlib

# local dependencies
from src.config import SIGNALLING_MODULES, DEBUG
from src.classes.colors import txcolors


def load_signals():
    signals = glob.glob("src/signals/*.exs")
    for filename in signals:
        for line in open(filename):
            try:
                os.remove(filename)
            except:
                if DEBUG:
                    print(f'{txcolors.WARNING}Could not remove external signalling file {filename}{txcolors.DEFAULT}')

    if os.path.isfile("src/signals/paused.exc"):
        try:
            os.remove("src/signals/paused.exc")
        except:
            if DEBUG:
                print(f'{txcolors.WARNING}Could not remove external signalling file {filename}{txcolors.DEFAULT}')

    my_module = {}

    # load signalling modules
    try:
        if len(SIGNALLING_MODULES) > 0:
            for module in SIGNALLING_MODULES:
                print(f'Starting {module}')
                my_module[module] = importlib.import_module(module)
                t = threading.Thread(target=my_module[module].do_work, args=())
                t.daemon = True
                t.start()
                time.sleep(2)
        else:
            print(f'No modules to load {SIGNALLING_MODULES}')
    except Exception as e:
        print(e)
