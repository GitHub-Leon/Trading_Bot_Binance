# use for environment variables
import os
import threading
import time
import sys

from tradingview_ta import TA_Handler, Interval

# local dependencies
from src.config import CUSTOM_LIST_FILE, DEBUG, PAIR_WITH, SIGNALS_FOLDER, bot_paused
from src.helpers.scripts.logger import debug_log

debug_log("Initialize OSC-Indicators, OSC-Threshold, MA-Indicators, MA-Threshold and Interval", False)
OSC_INDICATORS = ['Stoch.RSI', 'RSI']  # Indicators to use in Oscillator analysis
OSC_THRESHOLD = 2  # Must be less or equal to number of items in OSC_INDICATORS
MA_INDICATORS = ['SMA50', 'EMA50', 'EMA100']  # Indicators to use in Moving averages analysis
MA_THRESHOLD = 3  # Must be less or equal to number of items in MA_INDICATORS
INTERVAL = Interval.INTERVAL_15_MINUTES  # Timeframe for analysis

debug_log("Define Exchange, Screener and Time-to-wait", False)
EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
TIME_TO_WAIT = 4  # Minutes to wait between analysis


def analyze(pairs):
    signal_coins = {}
    analysis = {}
    handler = {}

    if os.path.exists(SIGNALS_FOLDER + '/buy_custom_2.exs'):
        os.remove(SIGNALS_FOLDER + '/buy_custom_2.exs')

    for pair in pairs:
        handler[pair] = TA_Handler(
            symbol=pair,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=INTERVAL,
            timeout=10)

    for pair in pairs:
        try:
            analysis = handler[pair].get_analysis()
        except Exception as e:  # outputs exceptions and details
            debug_log(
                f"Error while getting analysis.(custom_2.py) Error-Message: {str(e)} With coin: {pair} Handler: {handler[pair]}",
                True)
            if DEBUG:
                print("Custom_2:")
                print("Exception:")
                print(e)
                print(f'Coin: {pair}')
                print(f'handler: {handler[pair]}')

        oscCheck = 0
        maCheck = 0
        for indicator in OSC_INDICATORS:  # counts how many of the OSC_indicators result in a 'BUY'
            if analysis.oscillators['COMPUTE'][indicator] == 'BUY':
                oscCheck += 1

        for indicator in MA_INDICATORS:  # counts how many of the MA_indicators result in a 'BUY'
            if analysis.moving_averages['COMPUTE'][indicator] == 'BUY':
                maCheck += 1

        debug_log(f'Custom_2:{pair} Oscillators:{oscCheck}/{len(OSC_INDICATORS)} Moving averages:{maCheck}/{len(MA_INDICATORS)}', False)
        if DEBUG:
            print(
                f'Custom_2:{pair} Oscillators:{oscCheck}/{len(OSC_INDICATORS)} Moving averages:{maCheck}/{len(MA_INDICATORS)}')

        if oscCheck >= OSC_THRESHOLD and maCheck >= MA_THRESHOLD:  # writes the coins that should be bought in a file
            signal_coins[pair] = pair

            debug_log(f'Custom_2: Signal detected on {pair} at {oscCheck}/{len(OSC_INDICATORS)} oscillators and {maCheck}/{len(MA_INDICATORS)} moving averages.', False)
            if DEBUG:
                print(
                    f'Custom_2: Signal detected on {pair} at {oscCheck}/{len(OSC_INDICATORS)} oscillators and {maCheck}/{len(MA_INDICATORS)} moving averages.')

            debug_log("Read signal file custom-2.exs", False)
            with open(SIGNALS_FOLDER + '/buy_custom_2.exs', 'a+') as f:
                f.write(pair + '\n')

    return signal_coins


def do_work():
    signal_coins = {}
    pairs = {}

    pairs = [line.strip() for line in open(CUSTOM_LIST_FILE)]
    for line in open(CUSTOM_LIST_FILE):
        pairs = [line.strip() + PAIR_WITH for line in open(CUSTOM_LIST_FILE)]

    while True:
        try:
            if not threading.main_thread().is_alive() or bot_paused:  # kills itself, if the main bot isn't running or bot is paused
                exit()

            debug_log(f'Custom_2: Analyzing {len(pairs)} coins', False)
            if DEBUG:
                print(f'Custom_2: Analyzing {len(pairs)} coins')

            signal_coins = analyze(pairs)

            debug_log(f'Custom_2: {len(signal_coins)} coins above {OSC_THRESHOLD}/{len(OSC_INDICATORS)} oscillators and {MA_THRESHOLD}/{len(MA_INDICATORS)} moving averages Waiting {TIME_TO_WAIT} minutes for next analysis.', False)
            if DEBUG:
                print(
                    f'Custom_2: {len(signal_coins)} coins above {OSC_THRESHOLD}/{len(OSC_INDICATORS)} oscillators and {MA_THRESHOLD}/{len(MA_INDICATORS)} moving averages Waiting {TIME_TO_WAIT} minutes for next analysis.')

        except Exception as e:
            debug_log(f"Error in Module: {sys.argv[0]}. Restarting Module", True)
            if DEBUG:
                print(f'Error in Module: {sys.argv[0]}\n Restarting...')

        finally:  # wait, no matter if there's an error or not
            time.sleep((TIME_TO_WAIT * 60))

