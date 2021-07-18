# This module handles buys

import time
from datetime import datetime

from src.classes.TxColor import txcolors
from src.config import coins_bought, LOG_TRADES, TEST_MODE, client, TRADING_FEE, QUANTITY
from src.helpers.scripts import logger
from src.helpers.scripts.logger import debug_log, console_log
from src.strategies.default.convert_volume import convert_volume


def buy():
    """Place Buy market orders for each volatile coin found"""

    debug_log("Place buy market orders for each volatile coin found", False)

    volume, last_price = convert_volume()
    orders = {}

    for coin in volume:
        debug_log("Only buy if there are no active trades on the coin", False)
        # only buy if the there are no active trades on the coin
        if coin not in coins_bought:
            console_log(f"{txcolors.DEFAULT}Preparing to buy {volume[coin]} {coin}{txcolors.DEFAULT}")

            if TEST_MODE:
                # only make an imaginary buy order
                orders[coin] = [{
                    'symbol': coin,
                    'orderId': 0,
                    'time': datetime.now().timestamp()
                }]

                # update not sold coins
                from src.update_globals import update_session_fees
                update_session_fees(QUANTITY * TRADING_FEE/100)

                # Log trade
                if LOG_TRADES:
                    logger.trade_log(f"Buy : {volume[coin]} {coin} - {last_price[coin]['price']}")

                continue

            # try to create a real order if the test orders did not raise an exception
            debug_log("Try to create a real order if the test order did not raise an exception", False)
            try:
                buy_limit = client.create_order(
                    symbol=coin,
                    side='BUY',
                    type='MARKET',
                    quantity=volume[coin]
                )

            # error handling here in case position cannot be placed
            except Exception as e:
                debug_log("Position cannot be placed. Error-Message: " + str(e), True)

            # run the else block if the position has been placed and return order info
            else:
                debug_log("Get all orders", False)
                orders[coin] = client.get_all_orders(symbol=coin, limit=1)

                # binance sometimes returns an empty list, the code will wait here until binance returns the order
                debug_log("Waiting for binance", False)
                while not orders[coin]:
                    orders[coin] = client.get_all_orders(symbol=coin, limit=1)
                    time.sleep(1)

                else:
                    # Log trade
                    if LOG_TRADES:
                        debug_log("Log trades", False)
                        logger.trade_log(f"Buy : {volume[coin]} {coin} - {last_price[coin]['price']}")

    return orders, last_price, volume
