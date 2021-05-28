# use for environment variables
import os
# used for directory handling
import time

from tradingview_ta import TA_Handler, Interval

# local dependencies
from src.config import PAIR_WITH, SIGNALS_FILE, DEBUG, CUSTOM_LIST_FILE

MY_EXCHANGE = 'BINANCE'
MY_SCREENER = 'CRYPTO'
MY_FIRST_INTERVAL = Interval.INTERVAL_1_MINUTE
MY_SECOND_INTERVAL = Interval.INTERVAL_5_MINUTES
TA_BUY_THRESHOLD = 18  # How many of the 26 indicators to indicate a buy
TIME_TO_WAIT = 4  # Minutes to wait between analysis


def analyze(pairs):
    taMax = 0
    taMaxCoin = 'none'
    signal_coins = {}
    first_analysis = {}
    second_analysis = {}
    first_handler = {}
    second_handler = {}
    if os.path.exists(SIGNALS_FILE):
        os.remove(SIGNALS_FILE)

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
            print("Exeption:")
            print(e)
            print(f'Coin: {pair}')
            print(f'First handler: {first_handler[pair]}')
            print(f'Second handler: {second_handler[pair]}')
            tacheckS = 0

        first_tacheck = first_analysis.summary['BUY']
        second_tacheck = second_analysis.summary['BUY']
        if DEBUG:
            print(f'{pair} First {first_tacheck} Second {second_tacheck}')

        if first_tacheck > taMax:
            taMax = first_tacheck
            taMaxCoin = pair
        if first_tacheck >= TA_BUY_THRESHOLD and second_tacheck >= TA_BUY_THRESHOLD:
            signal_coins[pair] = pair

            if DEBUG:
                print(f'Signal detected on {pair}')

            with open(SIGNALS_FILE, 'a+') as f:
                f.write(pair + '\n')

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
        if DEBUG:
            print(f'Analyzing {len(pairs)} coins')

        signal_coins = analyze(pairs)

        if DEBUG:
            if len(signal_coins) == 0:
                print(f'No coins above {TA_BUY_THRESHOLD} threshold')
            else:
                print(f'{len(signal_coins)} coins above {TA_BUY_THRESHOLD} threshold on both timeframes')
                print(f'Waiting {TIME_TO_WAIT} minutes for next analysis')

        time.sleep((TIME_TO_WAIT * 60))
