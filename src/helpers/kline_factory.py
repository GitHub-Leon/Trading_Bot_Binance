# This function returns intervals depending on user input in config.yml

import time

# local dependencies
from src.config import client


def kline_factory_interval(interval):
    switcher = {
        "1min": client.KLINE_INTERVAL_1MINUTE,
        "3min": client.KLINE_INTERVAL_3MINUTE,
        "5min": client.KLINE_INTERVAL_5MINUTE,
        "15min": client.KLINE_INTERVAL_15MINUTE,
        "30min": client.KLINE_INTERVAL_30MINUTE,
        "1hour": client.KLINE_INTERVAL_1HOUR,
        "2hour": client.KLINE_INTERVAL_2HOUR,
        "4hour": client.KLINE_INTERVAL_4HOUR,
        "6hour": client.KLINE_INTERVAL_6HOUR,
        "8hour": client.KLINE_INTERVAL_8HOUR,
        "12hour": client.KLINE_INTERVAL_12HOUR,
        "1day": client.KLINE_INTERVAL_1DAY,
        "3day": client.KLINE_INTERVAL_3DAY,
        "1week": client.KLINE_INTERVAL_1WEEK,
        "1month": client.KLINE_INTERVAL_1MONTH
    }
    return switcher.get(interval, lambda: "invalid RSI Interval")


def kline_factory_timestamp(interval, period):
    switcher = {
        "1min": 60000,
        "3min": 180000,
        "5min": 300000,
        "15min": 1500000,
        "30min": 3000000,
        "1hour": 6000000,
        "2hour": 12000000,
        "4hour": 24000000,
        "6hour": 36000000,
        "8hour": 48000000,
        "12hour": 72000000,
        "1day": 144000000,
        "3day": 432000000,
        "1week": 1008000000,
        "1month": 4032000000
    }
    duration = switcher.get(interval, -1)

    # calculates backtrack for period
    current_time = round(time.time() * 1000)
    timestamp = current_time - period*duration

    return timestamp
