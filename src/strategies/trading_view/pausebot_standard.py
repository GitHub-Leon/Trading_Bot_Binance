import os
import threading
import time

from tradingview_ta import TA_Handler, Interval

# local dependencies
from src.config import SIGNALS_FOLDER
from src.helpers.scripts.logger import debug_log

INTERVAL = Interval.INTERVAL_1_MINUTE  # Timeframe for analysis

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
SYMBOL = 'BTCUSDT'
THRESHOLD = 7  # 7 of 15 MA's indicating sell
TIME_TO_WAIT = 5  # Minutes to wait between analysis


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
            f'Save-Mode: Market not looking too good, bot paused from buying {ma_sell}/{THRESHOLD} Waiting {TIME_TO_WAIT} minutes for next market checkup',
            False)
        print(
            f'Save-Mode: Market not looking too good, bot paused from buying {ma_sell}/{THRESHOLD} Waiting {TIME_TO_WAIT} minutes for next market checkup')
    else:
        debug_log(
            f'Save-Mode: Market looks ok, bot is running {ma_sell}/{THRESHOLD} Waiting {TIME_TO_WAIT} minutes for next market checkup ',
            False)
        print(
            f'Save-Mode: Market looks ok, bot is running {ma_sell}/{THRESHOLD} Waiting {TIME_TO_WAIT} minutes for next market checkup ')
        paused = False

    return paused


def do_work():
    while True:
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

        time.sleep((TIME_TO_WAIT * 60))
