from src.helpers.scripts.logger import debug_log, console_log
from src.config import DEBUG
import sys


def start_tradingview():
    try:
        debug_log(f"Trying to sell coin.", False)
        if DEBUG:
            console_log(f'Trying to sell coin.')

        use_limit_sell_order(coin, coins_sold, last_prices)

    except Exception as e:
        debug_log(f"Error in Module: {sys.argv[0]}. Couldn't cancel a limit sell order.", True)
        if DEBUG:
            console_log(f"Error in Module: {sys.argv[0]}\n. Couldn't cancel a limit sell order.")
