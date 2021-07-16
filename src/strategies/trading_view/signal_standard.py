# use for environment variables
import os
import threading
import time
import sys

from tradingview_ta import TA_Handler, Interval

# local dependencies
from src.config import PAIR_WITH, SIGNALS_FOLDER, DEBUG, CUSTOM_LIST_FILE
from src.strategies.trading_view import lock
from src.helpers.scripts.logger import debug_log

MY_EXCHANGE = 'BINANCE'
MY_SCREENER = 'CRYPTO'
MY_FIRST_INTERVAL = Interval.INTERVAL_5_MINUTES
MY_SECOND_INTERVAL = Interval.INTERVAL_15_MINUTES
TA_BUY_THRESHOLD = 11  # How many of the 26 indicators to indicate a buy
TIME_TO_WAIT = 4  # Minutes to wait between analysis


def analyze(pairs):
    with lock:
        debug_log(f"Analyze pairs", False)
    taMax = 0
    taMaxCoin = 'none'
    signal_coins = {}
    first_analysis = {}
    second_analysis = {}
    first_handler = {}
    second_handler = {}

    if os.path.exists(SIGNALS_FOLDER + '/buy_signal_standard.exs'):
        os.remove(SIGNALS_FOLDER + '/buy_signal_standard.exs')

    for pair in pairs:
        first_handler[pair] = TA_Handler(
            symbol=pair,
            exchange=MY_EXCHANGE,
            screener=MY_SCREENER,
            interval=MY_FIRST_INTERVAL,
            timeout=10
        )
        second_handler[pair] = TA_Handler(
            symbol=pair,
            exchange=MY_EXCHANGE,
            screener=MY_SCREENER,
            interval=MY_SECOND_INTERVAL,
            timeout=10
        )

    for pair in pairs:

        try:
            first_analysis = first_handler[pair].get_analysis()
            second_analysis = second_handler[pair].get_analysis()
        except Exception as e:
            with lock:
                debug_log(
                    f"Error while getting analysis.(signal_standard.py) Error-Message: {str(e)} With coin: {pair} First handler: {first_handler[pair]} Second handler: {second_handler[pair]}",
                    True)
            tacheckS = 0

        first_tacheck = first_analysis.summary['BUY']
        second_tacheck = second_analysis.summary['BUY']
        with lock:
            debug_log(f'{pair} First {first_tacheck} Second {second_tacheck}', False)
            if DEBUG:
                print(f'{pair} First {first_tacheck} Second {second_tacheck}')

        if first_tacheck > taMax:
            taMax = first_tacheck
            taMaxCoin = pair
        if first_tacheck >= TA_BUY_THRESHOLD and second_tacheck >= TA_BUY_THRESHOLD:
            signal_coins[pair] = pair

            with lock:
                debug_log(f'Signal detected on {pair}', False)
                if DEBUG:
                    print(f'Signal detected on {pair}')

            try:
                with open(SIGNALS_FOLDER + '/buy_signal_standard.exs', 'a+') as f:
                    f.write(pair + '\n')
            except OSError as e:
                with lock:
                    debug_log("Error while writing to signals file. Error-Message: " + str(e), True)

    with lock:
        debug_log(f'Max signal by {taMaxCoin} at {taMax} on shortest timeframe', False)
        if DEBUG:
            print(f'Max signal by {taMaxCoin} at {taMax} on shortest timeframe')

    return signal_coins


def do_work():
    signal_coins = {}
    pairs = {}

    pairs = [line.strip() for line in open(CUSTOM_LIST_FILE)]
    for line in open(CUSTOM_LIST_FILE):
        pairs = [line.strip() + PAIR_WITH for line in open(CUSTOM_LIST_FILE)]

    while True:
        try:
            if not threading.main_thread().is_alive():  # kills itself, if the main bot isn't running
                exit()

            with lock:
                debug_log(f'Analyzing {len(pairs)} coins', False)
                if DEBUG:
                    print(f'Analyzing {len(pairs)} coins')

            signal_coins = analyze(pairs)

            if len(signal_coins) == 0:
                with lock:
                    debug_log(f'No coins above {TA_BUY_THRESHOLD} threshold', False)
                    if DEBUG:
                        print(f'No coins above {TA_BUY_THRESHOLD} threshold')
            else:
                with lock:
                    debug_log(f'{len(signal_coins)} coins above {TA_BUY_THRESHOLD} threshold on both timeframes', False)
                    debug_log(f'Waiting {TIME_TO_WAIT} minutes for next analysis', False)
                    if DEBUG:
                        print(f'{len(signal_coins)} coins above {TA_BUY_THRESHOLD} threshold on both timeframes')
                        print(f'Waiting {TIME_TO_WAIT} minutes for next analysis')

        except Exception as e:
            with lock:
                debug_log(f"Error in Module: {sys.argv[0]}. Restarting Module", True)
                if DEBUG:
                    print(f'Error in Module: {sys.argv[0]}\n Restarting...')

        finally:  # wait, no matter if there's an error or not
            time.sleep((TIME_TO_WAIT * 60))
