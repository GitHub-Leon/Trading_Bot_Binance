import json
import os
from datetime import datetime

# local dependencies
from src.config import client, LOG_TRADES
from src.helpers.scripts import logger


def sell_all():
    logger.debug_log("Trying to sell all coins", False)
    # sells every coin in coins_bought.json and deletes file afterwards
    if os.path.exists('coins_bought.json'):
        with open('coins_bought.json', 'r') as f:
            coins = json.load(f)

            for coin in list(coins):
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
                    logger.debug_log("Log trades in log file", False)
                    timestamp = datetime.now().strftime("%d/%m %H:%M:%S")
                    logger.trade_log(
                        f"Sell: {coins[coin]['volume']} {coin} - {buy_price} - {last_price} Profit: {profit:.2f} {price_change:.2f}%")

        os.remove('coins_bought.json')

    # delete test_mode_coins_bought.json
    if os.path.exists('test_mode_coins_bought.json'):
        os.remove('test_mode_coins_bought.json')
