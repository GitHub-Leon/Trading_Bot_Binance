from tradingview_ta import TA_Handler, Interval
import os
import time
import threading
import sys

# local dependencies
from src.config import PAIR_WITH, CUSTOM_LIST_FILE, DEBUG, SIGNALS_FOLDER
from src.helpers.scripts.logger import debug_log

debug_log("Define Exchange, Screener and Time-to-wait", False)
MY_EXCHANGE = 'BINANCE'
MY_SCREENER = 'CRYPTO'
MY_FIRST_INTERVAL = Interval.INTERVAL_1_MINUTE
MY_SECOND_INTERVAL = Interval.INTERVAL_5_MINUTES
MY_THIRD_INTERVAL = Interval.INTERVAL_15_MINUTES
TA_BUY_THRESHOLD = 17  # How many of the 26 indicators to indicate a buy
TIME_TO_WAIT = 1  # Minutes to wait between analysis


def analyze(pairs):
    taMax = 0
    taMaxCoin = 'none'
    signal_coins = {}
    first_analysis = {}
    second_analysis = {}
    third_analysis = {}
    first_handler = {}
    second_handler = {}
    third_handler = {}

    if os.path.exists(SIGNALS_FOLDER + '/buy_custom_3.exs'):
        os.remove(SIGNALS_FOLDER + '/buy_custom_3.exs')

    if os.path.exists(SIGNALS_FOLDER + '/sell_custom_3.exs'):
        os.remove(SIGNALS_FOLDER + '/sell_custom_3.exs')

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
        third_handler[pair] = TA_Handler(
            symbol=pair,
            exchange=MY_EXCHANGE,
            screener=MY_SCREENER,
            interval=MY_THIRD_INTERVAL,
            timeout=10
        )

    for pair in pairs:

        try:
            first_analysis = first_handler[pair].get_analysis()
            second_analysis = second_handler[pair].get_analysis()
            third_analysis = third_handler[pair].get_analysis()
        except Exception as e:
            debug_log(
                f"Error while getting analysis.(custom_3.py) Error-Message: {str(e)} With coin: {pair}",
                True)
            if DEBUG:
                print("Custom_3:")
                print("Exception:")
                print(e)
                print(f'Coin: {pair}')
            tacheckS = 0

        first_tacheck = first_analysis.summary['BUY']
        first_recommendation = first_analysis.summary['RECOMMENDATION']
        first_RSI = float(first_analysis.indicators['RSI'])

        second_tacheck = second_analysis.summary['BUY']
        second_recommendation = second_analysis.summary['RECOMMENDATION']
        second_RSI = float(second_analysis.indicators['RSI'])

        third_tacheck = third_analysis.summary['BUY']
        third_recommendation = third_analysis.summary['RECOMMENDATION']
        third_RSI = float(third_analysis.indicators['RSI'])

        if DEBUG:
            print(f'custom_3:{pair} First {first_tacheck} Second {second_tacheck} Third {third_tacheck}')
            print(
                f'custom_3:{pair} First {first_recommendation} Second {second_recommendation} Third {third_recommendation}')
        # else:
        # print(".", end = '')

        if first_tacheck > taMax:
            taMax = first_tacheck
            taMaxCoin = pair

        '''if (first_recommendation == "BUY" or first_recommendation == "STRONG_BUY") and (second_recommendation == "BUY" or second_recommendation == "STRONG_BUY") and \
            (third_recommendation == "BUY" or third_recommendation == "STRONG_BUY"):
                if first_RSI <= 67 and second_RSI <= 67 and third_RSI <= 67:
                    signal_coins[pair] = pair
                    print(f'buysellcustsignal: Buy Signal detected on {pair}')
                    with open(SIGNALS_FOLDER + '/buy_custom_3.exs','a+') as f:
                        f.write(pair + '\n')'''

        if (first_recommendation == "SELL" or first_recommendation == "STRONG_SELL") and (
                second_recommendation == "SELL" or second_recommendation == "STRONG_SELL") and \
                (third_recommendation == "SELL" or third_recommendation == "STRONG_SELL"):
            # signal_coins[pair] = pair

            debug_log(f'custom_3: Sell Signal detected on {pair}', False)
            if DEBUG:
                print(f'custom_3: Sell Signal detected on {pair}')

            debug_log("Read signal file custom-2.exs", False)
            with open(SIGNALS_FOLDER + '/sell_custom_3.exs', 'a+') as f:
                f.write(pair + '\n')

    # print(f'buysellcustsignal: Max signal by {taMaxCoin} at {taMax} on shortest timeframe')

    return signal_coins


# if __name__ == '__main__':
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

            debug_log(f'custom_3: Analyzing {len(pairs)} coins', False)
            if DEBUG:
                print(f'custom_3: Analyzing {len(pairs)} coins')

            signal_coins = analyze(pairs)

            if len(signal_coins) == 0:
                debug_log(f'custom_3: No coins above {TA_BUY_THRESHOLD} threshold on three timeframes. Waiting {TIME_TO_WAIT} minutes for next analysis', False)
                if DEBUG:
                    print(
                        f'custom_3: No coins above {TA_BUY_THRESHOLD} threshold on three timeframes. Waiting {TIME_TO_WAIT} minutes for next analysis')
            else:
                debug_log(f'custom_3: {len(signal_coins)} coins above {TA_BUY_THRESHOLD} treshold on three timeframes. Waiting {TIME_TO_WAIT} minutes for next analysis', False)
                if DEBUG:
                    print(
                        f'custom_3: {len(signal_coins)} coins above {TA_BUY_THRESHOLD} treshold on three timeframes. Waiting {TIME_TO_WAIT} minutes for next analysis')

        except Exception as e:
            debug_log(f"Error in Module: {sys.argv[0]}. Restarting Module", True)
            if DEBUG:
                print(f'Error in Module: {sys.argv[0]}\n Restarting...')

        finally:  # wait, no matter if there's an error or not
            time.sleep((TIME_TO_WAIT * 60))
