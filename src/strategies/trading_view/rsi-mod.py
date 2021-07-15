import os
import threading
import time
import sys

from tradingview_ta import TA_Handler, Interval

# local dependencies
from src.config import PAIR_WITH, CUSTOM_LIST_FILE, SIGNALS_FOLDER, DEBUG, bot_paused
from src.helpers.scripts.logger import debug_log


INTERVAL = Interval.INTERVAL_15_MINUTES  # Main Timeframe for analysis on Oscillators and Moving Averages (15 mins)
INTERVAL2 = Interval.INTERVAL_5_MINUTES  # Secondary Timeframe for analysis on BUY signals for next lowest timescale | Check Entry Point (5)

OSC_INDICATORS = ['RSI', 'Stoch.RSI', 'Mom', 'MACD', 'UO', 'BBP']  # Indicators to use in Oscillator analysis
OSC_THRESHOLD = 5  # Must be less or equal to number of items in OSC_INDICATORS (5)
MA_INDICATORS = ['EMA10', 'EMA20', 'SMA10', 'SMA20']  # Indicators to use in Moving Averages analysis
MA_THRESHOLD = 3  # Must be less or equal to number of items in MA_INDICATORS (3)
MA_SUMMARY = 13  # Buy indicators out of 26 to use in Moving Averages INTERVAL analysis (13)
MA_SUMMARY2 = 13  # Buy indicators out of 26 to use in Moving Averages INTERVAL2 analysis (13)
OSC_SUMMARY = 2  # Sell indicators out of 11 to use in Oscillators analysis (2)

RSI_MIN = 12  # Min RSI Level for Buy Signal - Under 25 considered oversold (12)
RSI_MAX = 55  # Max RSI Level for Buy Signal - Over 80 considered overbought (55)
STOCH_MIN = 12  # Min Stoch %K Level for Buy Signal - Under 15 considered bearish until it crosses %D line (12)
STOCH_MAX = 99  # Max Stoch %K Level for Buy Signal - Over 80 ok as long as %D line doesn't cross %K (99)

RSI_BUY = 0.3  # Difference in RSI levels over last 2 timescales for a Buy Signal (-0.3)
STOCH_BUY = 10  # Difference between the Stoch K&D levels for a Buy Signal (10)

SELL_COINS = True  # Set to true if you want the module to sell coins immediately upon bearish signals (False)
RSI_SELL = -5  # Difference in RSI levels over last 2 timescales for a Sell Signal (-5)
STOCH_SELL = -10  # Difference between the Stoch D&K levels for a Sell Signal (-10)
SIGNALS_SELL = 7  # Max number of buy signals on both INTERVALs to add coin to sell list (7)

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
TIME_TO_WAIT = 2  # Minutes to wait between analysis


def analyze(pairs):
    signal_coins = {}
    analysis = {}
    handler = {}
    analysis2 = {}
    handler2 = {}

    if os.path.exists(SIGNALS_FOLDER + '/buy_rsi-mod.exs'):
        os.remove(SIGNALS_FOLDER + '/buy_rsi-mod.exs')

    if os.path.exists(SIGNALS_FOLDER + '/sell_rsi-mod.exs'):
        os.remove(SIGNALS_FOLDER + '/sell_rsi-mod.exs')

    for pair in pairs:
        handler[pair] = TA_Handler(
            symbol=pair,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=INTERVAL,
            timeout=10)

        handler2[pair] = TA_Handler(
            symbol=pair,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=INTERVAL2,
            timeout=10)

    for pair in pairs:
        try:
            analysis = handler[pair].get_analysis()
            analysis2 = handler2[pair].get_analysis()
        except Exception as e:
            debug_log(
                f"Error while getting analysis.(rsi-mod.py) Error-Message: {str(e)} With coin: {pair} Handler: {handler[pair]}",
                True)
            if DEBUG:
                print("rsi-mod:")
                print("Exception:")
                print(e)
                print(f'Coin: {pair}')
                print(f'handler: {handler[pair]}')

        oscCheck = 0
        maCheck = 0

        for indicator in OSC_INDICATORS:
            oscResult = analysis.oscillators['COMPUTE'][indicator]
            # print(f'{pair} - Indicator for {indicator} is {oscResult}')
            if analysis.oscillators['COMPUTE'][indicator] != 'SELL':
                oscCheck += 1

        for indicator in MA_INDICATORS:
            if analysis.moving_averages['COMPUTE'][indicator] == 'BUY':
                maCheck += 1

        # Stoch.RSI (19 - 99), RSI (19 - 69)
        RSI = round(analysis.indicators['RSI'], 2)
        RSI1 = round(analysis.indicators['RSI[1]'], 2)
        STOCH_K = round(analysis.indicators['Stoch.K'], 2)
        STOCH_D = round(analysis.indicators['Stoch.D'], 2)
        STOCH_K1 = round(analysis.indicators['Stoch.K[1]'], 2)
        STOCH_D1 = round(analysis.indicators['Stoch.D[1]'], 2)
        EMA10 = round(analysis.indicators['EMA10'], 2)
        EMA20 = round(analysis.indicators['EMA20'], 2)
        EMA30 = round(analysis.indicators['EMA30'], 2)
        SMA10 = round(analysis.indicators['SMA10'], 2)
        SMA20 = round(analysis.indicators['SMA20'], 2)
        SMA30 = round(analysis.indicators['SMA30'], 2)
        BUY_SIGS = round(analysis.summary['BUY'], 0)
        BUY_SIGS2 = round(analysis2.summary['BUY'], 0)
        STOCH_DIFF = round(STOCH_K - STOCH_D, 2)
        RSI_DIFF = round(RSI - RSI1, 2)

        if DEBUG:
            if (RSI < 80) and (BUY_SIGS >= 10) and (STOCH_DIFF >= 0.01) and (RSI_DIFF >= 0.01):
                print(
                    f'Signals OSC: {pair} = RSI:{RSI}/{RSI1} DIFF: {RSI_DIFF} | STOCH_K/D:{STOCH_K}/{STOCH_D} DIFF: {STOCH_DIFF} | BUYS: {BUY_SIGS}_{BUY_SIGS2}/26 | {oscCheck}-{maCheck}')


        if (RSI_MIN <= RSI <= RSI_MAX) and (RSI_DIFF >= RSI_BUY) and not bot_paused:
            if (STOCH_DIFF >= STOCH_BUY) and (STOCH_MIN <= STOCH_K <= STOCH_MAX) and (STOCH_MIN <= STOCH_D <= STOCH_MAX):
                if (BUY_SIGS >= MA_SUMMARY) and (BUY_SIGS2 >= MA_SUMMARY2) and (STOCH_K > STOCH_K1):
                    if oscCheck >= OSC_THRESHOLD and maCheck >= MA_THRESHOLD:
                        signal_coins[pair] = pair
                        debug_log(f'Signals RSI: {pair} - Buy Signal Detected | {BUY_SIGS}_{BUY_SIGS2}', False)
                        if DEBUG:
                            print(f'Signals RSI: {pair} - Buy Signal Detected | {BUY_SIGS}_{BUY_SIGS2}')
                        with open(SIGNALS_FOLDER + '/buy_rsi-mod.exs', 'a+') as f:
                            f.write(pair + '\n')
                else:
                    if DEBUG:
                        print(
                            f'Signals RSI: {pair} - Stoch/RSI ok, not enough buy signals | {BUY_SIGS}_{BUY_SIGS2}/26 | {STOCH_DIFF}/{RSI_DIFF} | {STOCH_K}')

        if SELL_COINS:
            if (BUY_SIGS < SIGNALS_SELL) and (BUY_SIGS2 < SIGNALS_SELL) and (STOCH_DIFF < STOCH_SELL) and (
                    RSI_DIFF < RSI_SELL) and (STOCH_K < STOCH_K1):
                # signal_coins[pair] = pair
                debug_log(f'Signals RSI: {pair} - Sell Signal Detected | {BUY_SIGS}_{BUY_SIGS2}', False)
                if DEBUG:
                    print(f'Signals RSI: {pair} - Sell Signal Detected | {BUY_SIGS}_{BUY_SIGS2}')
                with open(SIGNALS_FOLDER + '/sell_rsi-mod.exs', 'a+') as f:
                    f.write(pair + '\n')
            # else:
            #   print(f'Signal: {pair} - Not selling!')

    return signal_coins


def do_work():
    signal_coins = {}
    pairs = {}

    pairs = [line.strip() for line in open(CUSTOM_LIST_FILE)]
    for line in open(CUSTOM_LIST_FILE):
        pairs = [line.strip() + PAIR_WITH for line in open(CUSTOM_LIST_FILE)]

    while True:
        try:
            if not threading.main_thread().is_alive():
                exit()

            debug_log(f'Signals RSI: Analyzing {len(pairs)} coins', False)
            if DEBUG:
                print(f'Signals RSI: Analyzing {len(pairs)} coins')

            signal_coins = analyze(pairs)
            debug_log(f'Signals RSI: {len(signal_coins)} coins with Buy Signals. Waiting {TIME_TO_WAIT} minutes for next analysis.', False)
            if DEBUG:
                print(f'Signals RSI: {len(signal_coins)} coins with Buy Signals. Waiting {TIME_TO_WAIT} minutes for next analysis.')

        except Exception as e:
            debug_log(f"Error in Module: {sys.argv[0]}. Restarting Module", True)
            if DEBUG:
                print(f'Error in Module: {sys.argv[0]}\n Restarting...')

        finally:  # wait, no matter if there's an error or not
            time.sleep((TIME_TO_WAIT * 60))

