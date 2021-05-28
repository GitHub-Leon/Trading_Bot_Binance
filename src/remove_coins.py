# This module removes coins from portfolio

import json

# local dependencies
from src.config import coins_bought, coins_bought_file_path, QUANTITY, LOG_TRADES
from src.classes.colors import txcolors


def remove_from_portfolio(coins_sold):
    """Remove coins sold due to SL or TP from portfolio"""
    from src.config import session_profit  # loads session_profit every time function gets called

    for coin in coins_sold:
        coins_bought.pop(coin)

    with open(coins_bought_file_path, 'w') as file:
        json.dump(coins_bought, file, indent=4)

    if coins_sold != {} and LOG_TRADES:
        if session_profit >= 0:
            print(f'Working... Session profit:{txcolors.SELL_PROFIT}{session_profit:.2f}%{txcolors.DEFAULT} Est:{txcolors.SELL_PROFIT}{(QUANTITY * session_profit)/ 100:.2f}${txcolors.DEFAULT}')
        if session_profit < 0:
            print(f'Working... Session profit:{txcolors.SELL_LOSS}{session_profit:.2f}%{txcolors.DEFAULT} Est:{txcolors.SELL_LOSS}{(QUANTITY * session_profit)/ 100:.2f}${txcolors.DEFAULT}')
