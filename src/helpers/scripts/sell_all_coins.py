import json
import os
import sys
from datetime import datetime

# local dependencies
from src.config import client, LOG_TRADES
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
                    f"{timestamp} Sell: {coins[coin]['volume']} {coin} - {buy_price} - {last_price} Profit: {profit:.2f} {price_change:.2f}%")

    # delete files who store current coins bought
    if os.path.exists('../test_mode_coins_bought.json'):
        os.remove('../test_mode_coins_bought.json')
    if os.path.exists('../coins_bought.json'):
        os.remove('../coins_bought.json')
