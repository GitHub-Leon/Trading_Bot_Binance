import numpy as np
import time
import os
import threading
from datetime import datetime

# local dependencies
from src.config import client, coins_bought, SIGNALS_FOLDER, CUSTOM_LIST_FILE, PAIR_WITH, DEBUG
from src.helpers.scripts.logger import debug_log
from src.strategies.default.get_price import get_price


MY_EXCHANGE = 'BINANCE'
MY_SCREENER = 'CRYPTO'
RSI_TIME_INTERVAL = client.KLINE_INTERVAL_5MINUTE
RSI_PERIOD = 14
RSI_SELL_TRIGGER = 70
RSI_BUY_TRIGGER = 30
#MY_FIRST_INTERVAL = Interval.INTERVAL_5_MINUTES
#MY_SECOND_INTERVAL = Interval.INTERVAL_1_MINUTE
TA_BUY_THRESHOLD = 5  # How many of the 26 indicators to indicate a buy
TIME_TO_WAIT = 4  # Minutes to wait between analysis


def kline_factory_timestamp(interval, period):
    switcher = {
        client.KLINE_INTERVAL_1MINUTE: 60000,
        client.KLINE_INTERVAL_3MINUTE: 180000,
        client.KLINE_INTERVAL_5MINUTE: 300000,
        client.KLINE_INTERVAL_15MINUTE: 1500000,
        client.KLINE_INTERVAL_30MINUTE: 3000000,
        client.KLINE_INTERVAL_1HOUR: 6000000,
        client.KLINE_INTERVAL_2HOUR: 12000000,
        client.KLINE_INTERVAL_4HOUR: 24000000,
        client.KLINE_INTERVAL_6HOUR: 36000000,
        client.KLINE_INTERVAL_8HOUR: 48000000,
        client.KLINE_INTERVAL_12HOUR: 72000000,
        client.KLINE_INTERVAL_1DAY: 144000000,
        client.KLINE_INTERVAL_3DAY: 432000000,
        client.KLINE_INTERVAL_1WEEK: 1008000000,
        client.KLINE_INTERVAL_1MONTH: 4032000000
    }
    duration = switcher.get(interval, -1)

    # calculates backtrack for period
    current_time = round(time.time() * 1000)
    timestamp = current_time - period*duration

    return timestamp


def get_rsi_series(coins):
    timestamp = kline_factory_timestamp(RSI_TIME_INTERVAL, RSI_PERIOD)
    coins_rsi = {}

    for coin in list(coins):
        series = client.get_historical_klines(coin, RSI_TIME_INTERVAL, timestamp)

        coins_rsi[coin] = {
            'price': coins[coin]['price'],
            'time': datetime.now(),
            'series': series
        }

    print(coins_rsi)
    return coins_rsi


def check_rsi_buy_signal(coins):
    coins_with_buy_signal = {}
    coins_rsi = get_rsi_series(coins)

    for coin in coins_rsi:
        rsi_result = rsi(coins_rsi[coin]['series'])

        # Filters out coins who triggers the buy signal
        if rsi_result > RSI_BUY_TRIGGER:
            coins_with_buy_signal[coin]['symbol'] = coin

    return coins_with_buy_signal


def check_rsi_sell_signal():
    coins_with_sell_signal = {}
    coins_rsi = get_rsi_series(list(coins_bought))

    for coin in coins_rsi:
        rsi_result = rsi(coin['symbol']['series'])

        # Filters out coins who triggers the sell signal from current coins
        if rsi_result < RSI_SELL_TRIGGER:
            coins_with_sell_signal[coin['symbol']] = coin

    return coins_with_sell_signal


# calculating RSI
def rsi(series):
    delta = series.diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[RSI_PERIOD - 1]] = np.mean(ups[:RSI_PERIOD])  # first value is sum of avg gains
    ups = ups.drop(ups.index[:(RSI_PERIOD - 1)])
    downs[downs.index[RSI_PERIOD - 1]] = np.mean(downs[:RSI_PERIOD])  # first value is sum of avg losses
    downs = downs.drop(downs.index[:(RSI_PERIOD - 1)])
    rs = ups.ewm(com=RSI_PERIOD - 1, min_periods=0, adjust=False, ignore_na=False).mean() / \
         downs.ewm(com=RSI_PERIOD - 1, min_periods=0, adjust=False, ignore_na=False).mean()
    return 100 - 100 / (1 + rs)


# calculating Stoch RSI
def stochrsi(series, period, smoothK=3, smoothD=3):
    # Calculate RSI
    delta = series.diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[period - 1]] = np.mean(ups[:period])  # first value is sum of avg gains
    ups = ups.drop(ups.index[:(period - 1)])
    downs[downs.index[period - 1]] = np.mean(downs[:period])  # first value is sum of avg losses
    downs = downs.drop(downs.index[:(period - 1)])
    rs = ups.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean() / \
         downs.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean()
    rsi = 100 - 100 / (1 + rs)

    # Calculate StochRSI
    stochrsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    stochrsi_K = stochrsi.rolling(smoothK).mean()
    stochrsi_D = stochrsi_K.rolling(smoothD).mean()

    return stochrsi, stochrsi_K, stochrsi_D


# calculating Stoch RSI
#  -- Same as the above function but uses EMA, not SMA
def stochrsi_ema(series, period, smoothK=3, smoothD=3):
    # Calculate RSI
    delta = series.diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[period - 1]] = np.mean(ups[:period])  # first value is sum of avg gains
    ups = ups.drop(ups.index[:(period - 1)])
    downs[downs.index[period - 1]] = np.mean(downs[:period])  # first value is sum of avg losses
    downs = downs.drop(downs.index[:(period - 1)])
    rs = ups.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean() / \
         downs.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean()
    rsi = 100 - 100 / (1 + rs)

    # Calculate StochRSI
    stochrsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    stochrsi_K = stochrsi.ewm(span=smoothK).mean()
    stochrsi_D = stochrsi_K.ewm(span=smoothD).mean()

    return stochrsi, stochrsi_K, stochrsi_D


def analyze_buy(pairs):
    coins_buy_signal = {}  # init

    if os.path.exists(SIGNALS_FOLDER + '/buy_rsi.exs'):
        os.remove(SIGNALS_FOLDER + '/buy_rsi.exs')

    coins_buy_signal = check_rsi_buy_signal(pairs)

    for pair in coins_buy_signal:
        try:
            with open(SIGNALS_FOLDER + '/buy_rsi.exs', 'a+') as f:
                f.write(pair + '\n')
        except OSError as e:
            debug_log("Error while writing to signals file. Error-Message: " + str(e), True)

    print(coins_buy_signal)
    return coins_buy_signal


def analyze_sell():
    coins_sell_signal = {}  # init

    if os.path.exists(SIGNALS_FOLDER + '/sell_rsi.exs'):
        os.remove(SIGNALS_FOLDER + '/sell_rsi.exs')

    coins_sell_signal = check_rsi_sell_signal()

    for pair in coins_sell_signal:
        try:
            with open(SIGNALS_FOLDER + '/buy_rsi.exs', 'a+') as f:
                f.write(pair + '\n')
        except OSError as e:
            debug_log("Error while writing to signals file. Error-Message: " + str(e), True)

    print(coins_sell_signal)
    return coins_sell_signal


def do_work():
    coins = {}

    coins = get_price()

    while True:
        if not threading.main_thread().is_alive():  # kills itself, if the main bot isn't running
            exit()

        debug_log(f'Analyzing {len(coins)} coins', False)
        if DEBUG:
            print(f'Analyzing {len(coins)} coins')

        signal_buy_coins = analyze_buy(coins)
        signal_sell_coins = analyze_sell()

        # Buy coins output
        if len(signal_buy_coins) == 0:
            debug_log(f'No coins below {RSI_BUY_TRIGGER} threshold', False)
            if DEBUG:
                print(f'No coins below {RSI_BUY_TRIGGER} threshold')
        else:
            debug_log(f'{len(signal_buy_coins)} coins below {RSI_BUY_TRIGGER} threshold', False)
            debug_log(f'Waiting {TIME_TO_WAIT} minutes for next analysis', False)
            if DEBUG:
                print(f'{len(signal_buy_coins)} coins below {RSI_BUY_TRIGGER} threshold')
                print(f'Waiting {TIME_TO_WAIT} minutes for next analysis')

        # Sell coins output
        if len(signal_sell_coins) == 0:
            debug_log(f'No coins above {RSI_SELL_TRIGGER} threshold', False)
            if DEBUG:
                print(f'No coins above {RSI_SELL_TRIGGER} threshold')
        else:
            debug_log(f'{len(signal_sell_coins)} coins above {RSI_SELL_TRIGGER} threshold', False)
            debug_log(f'Waiting {TIME_TO_WAIT} minutes for next analysis', False)
            if DEBUG:
                print(f'{len(signal_sell_coins)} coins above {RSI_SELL_TRIGGER} threshold')
                print(f'Waiting {TIME_TO_WAIT} minutes for next analysis')

        time.sleep((TIME_TO_WAIT * 60))
