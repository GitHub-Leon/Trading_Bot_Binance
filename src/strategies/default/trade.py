# This module handles buys

import time
from datetime import datetime

from src.classes.colors import txcolors
from src.config import coins_bought, LOG_TRADES, TEST_MODE, client
from src.save_trade import write_log
# import local modules
from src.strategies.default.convert_volume import convert_volume


def buy():
    """Place Buy market orders for each volatile coin found"""

    volume, last_price = convert_volume()
    orders = {}

    for coin in volume:

        # only buy if the there are no active trades on the coin
        if coin not in coins_bought:
            print(f"{txcolors.DEFAULT}Preparing to buy {volume[coin]} {coin}{txcolors.DEFAULT}")

            if TEST_MODE:
                # only make an imaginary buy order
                orders[coin] = [{
                    'symbol': coin,
                    'orderId': 0,
                    'time': datetime.now().timestamp()
                }]

                # Log trade
                if LOG_TRADES:
                    write_log(f"Buy : {volume[coin]} {coin} - {last_price[coin]['price']}")

                continue

            # try to create a real order if the test orders did not raise an exception
            try:
                buy_limit = client.create_order(
                    symbol=coin,
                    side='BUY',
                    type='MARKET',
                    quantity=volume[coin]
                )

            # error handling here in case position cannot be placed
            except Exception as e:
                print(e)

            # run the else block if the position has been placed and return order info
            else:
                orders[coin] = client.get_all_orders(symbol=coin, limit=1)

                # binance sometimes returns an empty list, the code will wait here until binance returns the order
                while not orders[coin]:
                    orders[coin] = client.get_all_orders(symbol=coin, limit=1)
                    time.sleep(1)

                else:
                    # Log trade
                    if LOG_TRADES:
                        write_log(f"Buy : {volume[coin]} {coin} - {last_price[coin]['price']}")

    return orders, last_price, volume
