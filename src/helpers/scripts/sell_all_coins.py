import json
import os
import time

from src.config import client, LOG_TRADES, USE_LIMIT_ORDERS
from src.helpers.scripts.logger import debug_log, trade_log


def sell_all():
    debug_log("Trying to sell all coins", False)
    # sells every coin in coins_bought.json and deletes file afterwards
    if os.path.exists('coins_bought.json'):
        with open('coins_bought.json', 'r') as f:
            coins = json.load(f)

            for coin in list(coins):
                if len(client.get_open_orders(symbol=coin)) > 0:  # in case a buy order is still up, cancel it
                    orders = {coin: client.get_open_orders(symbol=coin)}
                    while not orders[coin]:
                        time.sleep(1)
                        orders[coin] = client.get_open_orders(symbol=coin)
                    sell_coin = client.cancel_order(
                        symbol=coin,
                        orderId=orders[coin][0]['orderId']
                    )

                try:
                    sell_coin = client.create_order(
                        symbol=coin,
                        side='SELL',
                        type='MARKET',
                        quantity=coins[coin]['volume']
                    )

                    buy_price = float(coins[coin]['bought_at'])
                    last_price = float(sell_coin['fills'][0]['price'])
                    profit = (last_price - buy_price) * coins[coin]['volume']
                    price_change = float((last_price - buy_price) / buy_price * 100)

                    if LOG_TRADES:
                        debug_log("Log trades in log file", False)
                        trade_log(
                            f"Sell: {coins[coin]['volume']} {coin} - {buy_price} - {last_price} Profit: {profit:.2f} {price_change:.2f}%")

                except Exception:
                    pass

        os.remove('coins_bought.json')

    # delete test_mode_coins_bought.json
    if os.path.exists('test_mode_coins_bought.json'):
        os.remove('test_mode_coins_bought.json')
