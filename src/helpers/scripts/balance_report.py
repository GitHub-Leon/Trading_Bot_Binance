# local dependencies
from src.config import QUANTITY, MAX_COINS, coins_bought, PAIR_WITH, LOG_TRADES
from src.helpers.decimals import decimals
from src.classes.TxColor import txcolors


def balance_report():
    from src.config import session_profit  # update value

    INVESTMENT_TOTAL = (QUANTITY * MAX_COINS)
    CURRENT_EXPOSURE = (QUANTITY * len(coins_bought))
    TOTAL_GAINS = ((QUANTITY * session_profit) / 100)
    NEW_BALANCE = (INVESTMENT_TOTAL + TOTAL_GAINS)
    INVESTMENT_GAIN = (TOTAL_GAINS / INVESTMENT_TOTAL) * 100

    if session_profit >= 0 and LOG_TRADES:
        print(f'Trade slots: {txcolors.WARNING}{len(coins_bought)}/{MAX_COINS} ({CURRENT_EXPOSURE:.{decimals()}f}'
              f'/{INVESTMENT_TOTAL:.{decimals()}f} {PAIR_WITH}){txcolors.DEFAULT} - '
              f'Profit: {txcolors.SELL_PROFIT}{session_profit:.2f}%{txcolors.DEFAULT} ({txcolors.SELL_PROFIT}{INVESTMENT_GAIN:.2f}%{txcolors.DEFAULT} - '
              f'{txcolors.SELL_PROFIT}{TOTAL_GAINS:.{decimals()}f}{PAIR_WITH}{txcolors.DEFAULT})')
    elif session_profit < 0 and LOG_TRADES:
        print(f'Trade slots: {txcolors.WARNING}{len(coins_bought)}/{MAX_COINS} ({CURRENT_EXPOSURE:.{decimals()}f}'
              f'/{INVESTMENT_TOTAL:.{decimals()}f} {PAIR_WITH}){txcolors.DEFAULT} - '
              f'Profit: {txcolors.SELL_LOSS}{session_profit:.2f}%{txcolors.DEFAULT} ({txcolors.SELL_LOSS}{INVESTMENT_GAIN:.2f}%{txcolors.DEFAULT} - '
              f'{txcolors.SELL_LOSS}{TOTAL_GAINS:.{decimals()}f}{PAIR_WITH}{txcolors.DEFAULT})')

    return
