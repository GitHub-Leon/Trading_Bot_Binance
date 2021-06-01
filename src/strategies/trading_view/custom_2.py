from tradingview_ta import TA_Handler, Interval

# use for environment variables
import os
import time
import threading

# local dependencies
from src.config import CUSTOM_LIST_FILE, DEBUG, PAIR_WITH, SIGNALS_FOLDER

OSC_INDICATORS = ['Stoch.RSI']  # Indicators to use in Oscillator analysis
OSC_THRESHOLD = 1  # Must be less or equal to number of items in OSC_INDICATORS
MA_INDICATORS = ['MA100', 'EMA100']  # Indicators to use in Moving averages analysis
MA_THRESHOLD = 2  # Must be less or equal to number of items in MA_INDICATORS
INTERVAL = Interval.INTERVAL_15_MINUTES  # Timeframe for analysis

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
TIME_TO_WAIT = 4  # Minutes to wait between analysis


def analyze(pairs):
    signal_coins = {}
    analysis = {}
    handler = {}

    if os.path.exists(SIGNALS_FOLDER + '/custom_2.exs'):
        os.remove(SIGNALS_FOLDER + '/custom_2.exs')

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

        if DEBUG:
            print(
                f'Custom_2:{pair} Oscillators:{oscCheck}/{len(OSC_INDICATORS)} Moving averages:{maCheck}/{len(MA_INDICATORS)}')

        if oscCheck >= OSC_THRESHOLD and maCheck >= MA_THRESHOLD:  # writes the coins that should be bought in a file
            signal_coins[pair] = pair

            if DEBUG:
                print(
                    f'Custom_2: Signal detected on {pair} at {oscCheck}/{len(OSC_INDICATORS)} oscillators and {maCheck}/{len(MA_INDICATORS)} moving averages.')

            with open(SIGNALS_FOLDER + '/custom_2.exs', 'a+') as f:
                f.write(pair + '\n')

    return signal_coins


def do_work():
    signal_coins = {}
    pairs = {}

    pairs = [line.strip() for line in open(CUSTOM_LIST_FILE)]
    for line in open(CUSTOM_LIST_FILE):
        pairs = [line.strip() + PAIR_WITH for line in open(CUSTOM_LIST_FILE)]

    while True:
        if not threading.main_thread().is_alive():  # kills itself, if the main bot isn't running
            exit()

        if DEBUG:
            print(f'Custom_2: Analyzing {len(pairs)} coins')

        signal_coins = analyze(pairs)

        if DEBUG:
            print(
                f'Custom_2: {len(signal_coins)} coins above {OSC_THRESHOLD}/{len(OSC_INDICATORS)} oscillators and {MA_THRESHOLD}/{len(MA_INDICATORS)} moving averages Waiting {TIME_TO_WAIT} minutes for next analysis.')

        time.sleep((TIME_TO_WAIT * 60))
