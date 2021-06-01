# This module removes coins from portfolio

import json

from src.classes.colors import txcolors
# local dependencies
from src.config import coins_bought, coins_bought_file_path, QUANTITY, LOG_TRADES
from src.helpers.scripts.logger import debug_log


def remove_from_portfolio(coins_sold):
    debug_log("Remove coins sold due to SL or TP from portfolio", False)
    """Remove coins sold due to SL or TP from portfolio"""

    from src.config import session_profit  # loads session_profit every time function gets called

    for coin in coins_sold:
        coins_bought.pop(coin)

    try:
        with open(coins_bought_file_path, 'w') as file:
            json.dump(coins_bought, file, indent=4)
    except OSError as e:
        debug_log("Error while reading coins_bought file", True)

    if coins_sold != {} and LOG_TRADES:
        if session_profit >= 0:
            debug_log(f'Working... Session profit:{txcolors.SELL_PROFIT}{session_profit:.2f}%{txcolors.DEFAULT} Est:{txcolors.SELL_PROFIT}{(QUANTITY * session_profit) / 100:.2f}${txcolors.DEFAULT}', False)
            print(
                f'Working... Session profit:{txcolors.SELL_PROFIT}{session_profit:.2f}%{txcolors.DEFAULT} Est:{txcolors.SELL_PROFIT}{(QUANTITY * session_profit) / 100:.2f}${txcolors.DEFAULT}')
        if session_profit < 0:
            debug_log(f'Working... Session profit:{txcolors.SELL_LOSS}{session_profit:.2f}%{txcolors.DEFAULT} Est:{txcolors.SELL_LOSS}{(QUANTITY * session_profit) / 100:.2f}${txcolors.DEFAULT}', False)
            print(
                f'Working... Session profit:{txcolors.SELL_LOSS}{session_profit:.2f}%{txcolors.DEFAULT} Est:{txcolors.SELL_LOSS}{(QUANTITY * session_profit) / 100:.2f}${txcolors.DEFAULT}')
