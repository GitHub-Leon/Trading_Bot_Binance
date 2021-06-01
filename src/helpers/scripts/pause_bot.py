import os
import time
from datetime import timedelta

# local dependencies
from src.classes.TxColor import txcolors
from src.config import TIME_DIFFERENCE, RECHECK_INTERVAL, QUANTITY, DEBUG, PAIR_WITH
from src.remove_coins import remove_from_portfolio
from src.strategies.default.get_price import get_price
from src.strategies.default.sell import sell_coins
from src.update_globals import update_bot_paused
from src.helpers.scripts.logger import debug_log
from src.helpers.decimals import decimals


def pause_bot():
    from src.config import bot_paused, session_profit, hsp_head

    debug_log("Pause the script when external indicators detect a bearish trend in the market", False)
    """Pause the script when external indicators detect a bearish trend in the market"""

    # start counting for how long the bot has been paused
    start_time = time.perf_counter()

    while os.path.isfile("src/signals/paused.exc"):

        if not bot_paused:
            debug_log("Pausing buying due to change in market conditions, stop loss and take profit will continue to work...", False)
            if DEBUG:
                print(
                    f'{txcolors.WARNING}Pausing buying due to change in market conditions, stop loss and take profit will continue to work...{txcolors.DEFAULT}')
            update_bot_paused(True)

        # Sell function needs to work even while paused
        debug_log("Init sell function while paused", False)
        coins_sold = sell_coins()
        remove_from_portfolio(coins_sold)
        get_price(True)

        # pausing here
        debug_log("Bot is pausing", False)
        if hsp_head == 1:
            debug_log(f'Paused... Session profit:{session_profit:.2f}% Est: {(QUANTITY * session_profit)/100:.{decimals()}f} {PAIR_WITH}', False)
            print(f'Paused... Session profit:{session_profit:.2f}% Est: {(QUANTITY * session_profit)/100:.{decimals()}f} {PAIR_WITH}')
        time.sleep((TIME_DIFFERENCE * 60) / RECHECK_INTERVAL)

    else:
        # stop counting the pause time
        stop_time = time.perf_counter()
        time_elapsed = timedelta(seconds=int(stop_time - start_time))

        # resume the bot and set pause_bot to False
        if bot_paused:
            debug_log(f'Resuming buying due to change in market conditions, total sleep time: {time_elapsed}', False)
            print(
                f'{txcolors.WARNING}Resuming buying due to change in market conditions, total sleep time: {time_elapsed}{txcolors.DEFAULT}')
            update_bot_paused(False)

    return
