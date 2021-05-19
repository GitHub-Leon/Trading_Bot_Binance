# This module fetches prices from binance API

from datetime import datetime

# local dependencies
from src.config import CUSTOM_LIST, PAIR_WITH, FIATS, client, tickers


def get_price():
    """Return the current price for all coins on binance"""

    initial_price = {}
    prices = client.get_all_tickers()

    for coin in prices:
        # Only return USDT pairs and exclude margin symbols like BTCDOWNUSDT, filter by custom list if defined.
        if CUSTOM_LIST:
            coin_is_in_ticker = any(item + PAIR_WITH in coin['symbol'] for item in tickers)
        else:  # only Return coin(PAIR_WITH) pairs and exclude margin symbols like BTCDOWNUSDT
            coin_is_in_ticker = PAIR_WITH in coin['symbol']

        coin_is_not_in_blocklist = all(item not in coin['symbol'] for item in FIATS)

        if coin_is_in_ticker and coin_is_not_in_blocklist:
            initial_price[coin['symbol']] = {
                'price': coin['price'],
                'time': datetime.now(),
            }

    return initial_price
