# This module removes coins from portfolio

import json

# local dependencies
from src.config import coins_bought, coins_bought_file_path
from src.helpers.scripts.logger import debug_log, console_log


def remove_from_portfolio(coins_sold):
    """Remove coins sold due to SL or TP from portfolio"""

    debug_log("Remove coins sold due to SL or TP from portfolio", False)

    for coin in coins_sold:
        coins_bought.pop(coin)

    with open(coins_bought_file_path, 'w') as file:
        json.dump(coins_bought, file, indent=4)
