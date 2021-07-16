# local dependencies
from src.classes.TxColor import txcolors
from src.config import QUANTITY, MAX_COINS, PAIR_WITH, LOG_TRADES, lock
from src.helpers.decimals import decimals


def balance_report(coins_sold):
    from src.config import session_profit, coins_bought  # update value

    INVESTMENT_TOTAL = (QUANTITY * MAX_COINS)
    CURRENT_EXPOSURE = (QUANTITY * (len(coins_bought) - len(coins_sold)))
    TOTAL_GAINS = ((QUANTITY * session_profit) / 100)
    NEW_BALANCE = (INVESTMENT_TOTAL + TOTAL_GAINS)
    INVESTMENT_GAIN = (TOTAL_GAINS / INVESTMENT_TOTAL) * 100

    if session_profit >= 0 and LOG_TRADES:
        with lock:
            print(
                f'Trade slots: {txcolors.WARNING}{len(coins_bought) - len(coins_sold)}/{MAX_COINS} ({CURRENT_EXPOSURE:.{decimals()}f}'
                f'/{INVESTMENT_TOTAL:.{decimals()}f} {PAIR_WITH}){txcolors.DEFAULT} - '
                f'Profit: {txcolors.SELL_PROFIT}{session_profit:.2f}%{txcolors.DEFAULT} ({txcolors.SELL_PROFIT}{INVESTMENT_GAIN:.2f}%{txcolors.DEFAULT} - '
                f'{txcolors.SELL_PROFIT}{TOTAL_GAINS:.{decimals()}f}{PAIR_WITH}{txcolors.DEFAULT})')
    elif session_profit < 0 and LOG_TRADES:
        with lock:
            print(
                f'Trade slots: {txcolors.WARNING}{len(coins_bought) - len(coins_sold)}/{MAX_COINS} ({CURRENT_EXPOSURE:.{decimals()}f}'
                f'/{INVESTMENT_TOTAL:.{decimals()}f} {PAIR_WITH}){txcolors.DEFAULT} - '
                f'Profit: {txcolors.SELL_LOSS}{session_profit:.2f}%{txcolors.DEFAULT} ({txcolors.SELL_LOSS}{INVESTMENT_GAIN:.2f}%{txcolors.DEFAULT} - '
                f'{txcolors.SELL_LOSS}{TOTAL_GAINS:.{decimals()}f}{PAIR_WITH}{txcolors.DEFAULT})')
