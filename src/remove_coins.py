# This module removes coins from portfolio

import json

# local dependencies
from src.config import coins_bought, coins_bought_file_path


def remove_from_portfolio(coins_sold):
    """Remove coins sold due to SL or TP from portfolio"""

    if coins_sold is None:
        return

    for coin in coins_sold:
        coins_bought.pop(coin)

    with open(coins_bought_file_path, 'w') as file:
        json.dump(coins_bought, file, indent=4)
