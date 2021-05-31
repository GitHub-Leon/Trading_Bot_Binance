# local dependencies
from src.config import QUANTITY, MAX_COINS, coins_bought, PAIR_WITH
from src.helpers.decimals import decimals


def balance_report():
    from src.config import session_profit  # update value

    INVESTMENT_TOTAL = (QUANTITY * MAX_COINS)
    CURRENT_EXPOSURE = (QUANTITY * len(coins_bought))
    TOTAL_GAINS = ((QUANTITY * session_profit) / 100)
    NEW_BALANCE = (INVESTMENT_TOTAL + TOTAL_GAINS)
    INVESTMENT_GAIN = (TOTAL_GAINS / INVESTMENT_TOTAL) * 100

    print(f'Trade slots: {len(coins_bought)}/{MAX_COINS} ({CURRENT_EXPOSURE:.{decimals()}f}/{INVESTMENT_TOTAL:.{decimals()}f} {PAIR_WITH}) - Profit: {session_profit:.2f}% ({INVESTMENT_GAIN:.2f}% - {TOTAL_GAINS:.{decimals()}f}{PAIR_WITH})')

    return
