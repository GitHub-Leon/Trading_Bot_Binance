import json
import os
from datetime import datetime
import sys

# local dependencies
from src.config import coins_bought, client, LOG_TRADES
from src.save_trade import write_log


def sell_all():
    sys.path.append('..')

    with open('../coins_bought.json', 'r') as f:
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
                timestamp = datetime.now().strftime("%d/%m %H:%M:%S")
                write_log(
                    f"Sell: {coins[coin]['volume']} {coin} - {buy_price} - {last_price} Profit: {profit:.2f} {price_change:.2f}%")

    os.remove('../coins_bought.json')
