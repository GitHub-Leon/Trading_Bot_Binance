import numpy as np
import time

# local dependencies
from src.config import client, coins_bought
from datetime import datetime


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
    rsi_coins = {}

    for coin in coins:
        series = client.get_historical_klines(coin['symbol'], RSI_TIME_INTERVAL, timestamp)

        rsi_coins[coin['symbol']] = {
            'price': coin['price'],
            'time': datetime.now(),
            'series': series
        }

    return rsi_coins


def check_rsi_buy_signal(coins_rsi):
    coins_with_buy_signal = {}

    for coin in coins_rsi:
        rsi_result = rsi(coin['symbol']['series'])

        # Filters out coins who triggers the buy signal
        if rsi_result > RSI_BUY_TRIGGER:
            coins_with_buy_signal[coin['symbol']] = coin

    return coins_with_buy_signal


def check_rsi_sell_signal():
    coins_with_sell_signal = {}

    for coin in list(coins_bought):
        rsi_result = rsi(coin['symbol']['series'])

        # Filters out coins who triggers the sell signal from current coins
        if rsi_result < RSI_SELL_TRIGGER:
            coins_with_sell_signal[coin['symbol']] = coin

    return coins_with_sell_signal


# calculating RSI
def rsi(series, period):
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
