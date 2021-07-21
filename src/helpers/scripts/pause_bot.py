import os
import sys
import threading
import time
from datetime import timedelta

from src.classes.TxColor import txcolors
from src.config import TIME_DIFFERENCE, RECHECK_INTERVAL, DEBUG, SIGNALS_FOLDER
from src.helpers.scripts.logger import debug_log, console_log
from src.update_globals import update_bot_paused

# local var
start_time = time.perf_counter()


def pause_bot():
    """Pause the script when external indicators detect a bearish trend in the market"""
    from src.config import bot_paused

    debug_log("Pause the script when external indicators detect a bearish trend in the market", False)

    # start counting for how long the bot has been paused
    start_time = time.perf_counter()

    while os.path.isfile(SIGNALS_FOLDER + "/paused.exc"):
        if not bot_paused:
            debug_log(
                "Pausing buying due to change in market conditions, stop loss and take profit will continue to work...",
                False)
            if DEBUG:
                console_log(
                    f'{txcolors.WARNING}Pausing buying due to change in market conditions, stop loss and take profit will continue to work...{txcolors.DEFAULT}')
            update_bot_paused(True)

        time.sleep((TIME_DIFFERENCE * 60) / RECHECK_INTERVAL)

    else:
        from src.config import bot_paused  # update glob var for print and debug_log
        # stop counting the pause time
        stop_time = time.perf_counter()
        time_elapsed = timedelta(seconds=int(stop_time - start_time))

        # resume the bot and set pause_bot to False
        if bot_paused:
            debug_log(f'Resuming buying due to change in market conditions, total sleep time: {time_elapsed}', False)
            console_log(
                f'{txcolors.WARNING}Resuming buying due to change in market conditions, total sleep time: {time_elapsed}{txcolors.DEFAULT}')
            update_bot_paused(False)

    return


def do_work():
    while True:
        try:
            if not threading.main_thread().is_alive():
                exit()

            pause_bot()

        except Exception as e:
            debug_log(f"Error in Module: {sys.argv[0]}. Restarting Module", True)
            if DEBUG:
                console_log(f'Error in Module: {sys.argv[0]}\n Restarting...')

        finally:  # wait, no matter if there's an error or not
            time.sleep(1)
