# This module fetches prices from binance API

import re
from datetime import datetime

from src.config import CUSTOM_LIST, PAIR_WITH, FIATS, client, tickers, RECHECK_INTERVAL, USE_LEVERAGE
from src.helpers.scripts.logger import debug_log
from src.update_globals import update_hsp_head, update_historical_prices


def get_price(add_to_historical=True):
    """Return the current price for all coins on binance"""

    debug_log("Get price", False)

    initial_price = {}
    prices = client.get_all_tickers()

    debug_log("Check prices for all coins in tickers file", False)

    for coin in prices:

        if USE_LEVERAGE and (re.match(r'.*DOWNUSDT$', coin['symbol']) or re.match(r'.*UPUSDT$', coin['symbol'])):
            initial_price[coin['symbol']] = {'price': coin['price'], 'time': datetime.now()}
        elif CUSTOM_LIST:
            if any(item + PAIR_WITH == coin['symbol'] for item in tickers) and all(
                    item not in coin['symbol'] for item in FIATS):
                initial_price[coin['symbol']] = {'price': coin['price'], 'time': datetime.now()}
        else:
            if PAIR_WITH in coin['symbol'] and all(item not in coin['symbol'] for item in FIATS):
                initial_price[coin['symbol']] = {'price': coin['price'], 'time': datetime.now()}

    if add_to_historical:
        from src.config import hsp_head  # import to init value
        update_hsp_head(hsp_head + 1)

        from src.config import hsp_head  # import hsp_head again to update value
        if hsp_head == RECHECK_INTERVAL:
            update_hsp_head(0)

        from src.config import hsp_head  # import hsp_head again to update value
        update_historical_prices(initial_price, hsp_head)

    return initial_price
