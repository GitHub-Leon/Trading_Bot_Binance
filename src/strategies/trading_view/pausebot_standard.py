import os
import sys
import threading
import time

from tradingview_ta import TA_Handler, Interval

from src.config import SIGNALS_FOLDER, SELL_WHEN_BEARISH, DEBUG
from src.helpers.scripts.logger import debug_log, console_log
from src.update_globals import update_sell_bearish

INTERVAL = Interval.INTERVAL_5_MINUTES  # Timeframe for analysis

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
SYMBOL = 'BTCUSDT'
THRESHOLD = 7  # x of 15 MA's indicating sell
TIME_TO_WAIT = 1  # Minutes to wait between analysis


def analyze():
    analysis = {}
    handler = {}

    handler = TA_Handler(
        symbol=SYMBOL,
        exchange=EXCHANGE,
        screener=SCREENER,
        interval=INTERVAL,
        timeout=10)

    try:
        analysis = handler.get_analysis()
    except Exception as e:
        debug_log("Error while pausebotmod. Error-Message:" + str(e), True)

    ma_sell = analysis.moving_averages['SELL']
    if ma_sell >= THRESHOLD:
        paused = True
        debug_log(
            f'Save-Mode: Market not looking too good, bot paused from buying {ma_sell}/{THRESHOLD} -> Waiting {TIME_TO_WAIT} minutes for next market checkup',
            False)
        console_log(
            f'Save-Mode: Market not looking too good, bot paused from buying {ma_sell}/{THRESHOLD} -> Waiting {TIME_TO_WAIT} minutes for next market checkup')
    else:
        debug_log(
            f'Save-Mode: Market looks ok, bot is running {ma_sell}/{THRESHOLD} -> Waiting {TIME_TO_WAIT} minutes for next market checkup ',
            False)
        console_log(
            f'Save-Mode: Market looks ok, bot is running {ma_sell}/{THRESHOLD} -> Waiting {TIME_TO_WAIT} minutes for next market checkup ')
        paused = False

    # Sells all coins if SELL_WHEN_BEARISH is True and market turns bearish
    if paused and SELL_WHEN_BEARISH:
        update_sell_bearish(True)
    elif not paused and SELL_WHEN_BEARISH:
        update_sell_bearish(False)

    return paused


def do_work():
    while True:
        try:
            if not threading.main_thread().is_alive():
                exit()

            paused = analyze()
            try:
                if paused:
                    with open(SIGNALS_FOLDER + '/paused.exc', 'a+') as f:
                        f.write('yes')
                else:
                    if os.path.isfile(SIGNALS_FOLDER + '/paused.exc'):
                        os.remove(SIGNALS_FOLDER + '/paused.exc')
            except OSError as e:
                debug_log("Error while writing or removing signal file. Error-Message: " + str(e), True)

        except Exception as e:
            debug_log(f"Error in Module: {sys.argv[0]}. Restarting Module", True)
            if DEBUG:
                console_log(f'Error in Module: {sys.argv[0]}\n Restarting...')

        finally:  # wait, no matter if there's an error or not
            time.sleep((TIME_TO_WAIT * 60))
