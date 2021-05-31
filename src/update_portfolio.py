import json

# local dependencies
from src.config import coins_bought, coins_bought_file_path, STOP_LOSS, TAKE_PROFIT, DEBUG
from src.helpers.scripts.balance_report import balance_report


def update_portfolio(orders, last_price, volume):
    """add every coin bought to our portfolio for tracking/selling later"""

    for coin in orders:

        coins_bought[coin] = {
            'symbol': orders[coin][0]['symbol'],
            'orderid': orders[coin][0]['orderId'],
            'timestamp': orders[coin][0]['time'],
            'bought_at': last_price[coin]['price'],
            'volume': volume[coin],
            'stop_loss': -STOP_LOSS,
            'take_profit': TAKE_PROFIT,
        }

        # save the coins in a json file in the same directory
        with open(coins_bought_file_path, 'w') as file:
            json.dump(coins_bought, file, indent=4)

        if DEBUG:
            print(f'Order with id {orders[coin][0]["orderId"]} placed and saved to file')
