import numpy as np

# local dependencies
from src.config import client, RSI_TIME_INTERVAL, RSI_PERIOD, RSI_SELL_TRIGGER, RSI_BUY_TRIGGER, coins_bought
from src.helpers.kline_factory import kline_factory_interval, kline_factory_timestamp
from datetime import datetime


def get_rsi_series(coins):
    interval = kline_factory_interval(RSI_TIME_INTERVAL)
    timestamp = kline_factory_timestamp(RSI_TIME_INTERVAL, RSI_PERIOD)
    rsi_coins = {}

    for coin in coins:
        series = client.get_historical_klines(coin['symbol'], interval, timestamp)

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
