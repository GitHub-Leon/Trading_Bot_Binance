import json

from src.config import coins_bought, coins_bought_file_path, STOP_LOSS, TAKE_PROFIT, DEBUG
from src.helpers.scripts.logger import debug_log, console_log


def update_portfolio(orders, last_price, volume):
    """add every coin bought to our portfolio for tracking/selling later"""

    debug_log("Add every coin bought to our portfolio for tracking/selling later", False)

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
        debug_log("Save the coins in the file", False)
        try:
            with open(coins_bought_file_path, 'w') as file:
                json.dump(coins_bought, file, indent=4)
        except OSError as e:
            debug_log("Error while writing coins to file. Error-Message: " + str(e), True)

        debug_log(f'Order with id {orders[coin][0]["orderId"]} placed and saved to file', False)
        if DEBUG:
            console_log(f'Order with id {orders[coin][0]["orderId"]} placed and saved to file')
