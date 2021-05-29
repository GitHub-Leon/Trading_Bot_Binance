import os
import threading
import time

from tradingview_ta import TA_Handler, Interval

from src.config import SIGNALS_FOLDER

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
        print("pausebotmod:")
        print("Exception:")
        print(e)

    ma_sell = analysis.moving_averages['SELL']
    if ma_sell >= THRESHOLD:
        paused = True
        print(
            f'Save-Mode: Market not looking too good, bot paused from buying {ma_sell}/{THRESHOLD} Waiting {TIME_TO_WAIT} minutes for next market checkup')
    else:
        print(
            f'Save-Mode: Market looks ok, bot is running {ma_sell}/{THRESHOLD} Waiting {TIME_TO_WAIT} minutes for next market checkup ')
        paused = False

    return paused


def do_work():
    while True:
        if not threading.main_thread().is_alive():
            exit()

        paused = analyze()
        if paused:
            with open(SIGNALS_FOLDER + '/paused.exc', 'a+') as f:
                f.write('yes')
        else:
            if os.path.isfile(SIGNALS_FOLDER + '/paused.exc'):
                os.remove(SIGNALS_FOLDER + '/paused.exc')

        time.sleep((TIME_TO_WAIT * 60))
