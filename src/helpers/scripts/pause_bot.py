import os
from datetime import timedelta
import time

# local dependencies
from src.classes.colors import txcolors
from src.strategies.default.sell import sell_coins
from src.remove_coins import remove_from_portfolio
from src.strategies.default.get_price import get_price
from src.update_globals import update_bot_paused
from src.config import TIME_DIFFERENCE, RECHECK_INTERVAL, QUANTITY, bot_paused, session_profit, hsp_head


def pause_bot():
    """Pause the script when external indicators detect a bearish trend in the market"""

    # start counting for how long the bot's been paused
    start_time = time.perf_counter()

    while os.path.isfile("signals/paused.exc"):

        if not bot_paused:
            print(f'{txcolors.WARNING}Pausing buying due to change in market conditions, stop loss and take profit will continue to work...{txcolors.DEFAULT}')
            update_bot_paused(True)

        # Sell function needs to work even while paused
        coins_sold = sell_coins()
        remove_from_portfolio(coins_sold)
        get_price(True)

        # pausing here
        if hsp_head == 1:
            print(f'Paused... Session profit:{session_profit:.2f}% Est:${(QUANTITY * session_profit) / 100:.2f}')
        time.sleep((TIME_DIFFERENCE * 60) / RECHECK_INTERVAL)

    else:
        # stop counting the pause time
        stop_time = time.perf_counter()
        time_elapsed = timedelta(seconds=int(stop_time - start_time))

        # resume the bot and ser pause_bot to False
        if bot_paused:
            print(f'{txcolors.WARNING}Resuming buying due to change in market conditions, total sleep time: {time_elapsed}{txcolors.DEFAULT}')
            update_bot_paused(False)

    return
