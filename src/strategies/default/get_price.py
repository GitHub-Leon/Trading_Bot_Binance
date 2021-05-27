# This module fetches prices from binance API

from datetime import datetime

# local dependencies
from src.config import CUSTOM_LIST, PAIR_WITH, FIATS, client, tickers, RECHECK_INTERVAL, hsp_head
from src.update_globals import update_hsp_head, update_historical_prices


def get_price(add_to_historical=True):
    """Return the current price for all coins on binance"""
    initial_price = {}
    prices = client.get_all_tickers()

    for coin in prices:

        if CUSTOM_LIST:
            if any(item + PAIR_WITH == coin['symbol'] for item in tickers) and all(
                    item not in coin['symbol'] for item in FIATS):
                initial_price[coin['symbol']] = {'price': coin['price'], 'time': datetime.now()}
        else:
            if PAIR_WITH in coin['symbol'] and all(item not in coin['symbol'] for item in FIATS):
                initial_price[coin['symbol']] = {'price': coin['price'], 'time': datetime.now()}

    if add_to_historical:
        update_hsp_head(hsp_head + 1)

        if hsp_head == RECHECK_INTERVAL:
            update_hsp_head(0)

        update_historical_prices(initial_price, hsp_head)

    return initial_price
