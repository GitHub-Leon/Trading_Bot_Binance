# This module calculated price differences and executes the sell_coins function once a threshold is reached

import time
from datetime import datetime, timedelta

# local dependencies
from src.classes.TxColor import txcolors
from src.config import PAIR_WITH, TIME_DIFFERENCE, RECHECK_INTERVAL, CHANGE_IN_PRICE, coins_bought, MAX_COINS, USE_DEFAULT_STRATEGY
from src.helpers.scripts.logger import debug_log
from src.helpers.scripts.pause_bot import pause_bot
from src.strategies.default.get_price import get_price
from src.strategies.external_signals import external_buy_signals
from src.update_globals import update_volatility_cooloff


def wait_for_price():
    from src.config import hsp_head, volatility_cooloff, historical_prices

    debug_log("Call the initial price and ensure the correct amount of time has passed before the current price again",
              False)
    """calls the initial price and ensures the correct amount of time has passed
    before reading the current price again"""

    volatile_coins = {}
    externals = {}

    coins_up = 0
    coins_down = 0
    coins_unchanged = 0

    pause_bot()

    if historical_prices[hsp_head]['BNB' + PAIR_WITH]['time'] > datetime.now() - timedelta(
            minutes=float(TIME_DIFFERENCE / RECHECK_INTERVAL)):
        # sleep for exactly the amount of time required
        debug_log("Sleep for exactly the amount of time required", False)
        time.sleep((timedelta(minutes=float(TIME_DIFFERENCE / RECHECK_INTERVAL)) - (
                datetime.now() - historical_prices[hsp_head]['BNB' + PAIR_WITH]['time'])).total_seconds())

    # retrieve latest prices
    get_price()

    # calculate the difference in prices
    debug_log("Calculate the difference in prices", False)
    for coin in historical_prices[hsp_head]:

        # minimum and maximum prices over time period
        min_price = min(historical_prices, key=lambda x: float("inf") if x is None else float(x[coin]['price']))
        max_price = max(historical_prices, key=lambda x: -1 if x is None else float(x[coin]['price']))

        threshold_check = (-1.0 if min_price[coin]['time'] > max_price[coin]['time'] else 1.0) * (
                float(max_price[coin]['price']) - float(min_price[coin]['price'])) / float(
            min_price[coin]['price']) * 100

        # each coin with higher gains than our CHANGE_IN_PRICE is added to the volatile_coins dict if less than MAX_COINS is not reached.
        if threshold_check > CHANGE_IN_PRICE:
            coins_up += 1

            if coin not in volatility_cooloff:
                update_volatility_cooloff(coin, datetime.now() - timedelta(minutes=TIME_DIFFERENCE))

            # only include coin as volatile if it hasn't been picked up in the last TIME_DIFFERENCE minutes already
            if datetime.now() >= volatility_cooloff[coin] + timedelta(minutes=TIME_DIFFERENCE):
                update_volatility_cooloff(coin, datetime.now())

                if USE_DEFAULT_STRATEGY:
                    if len(coins_bought) + len(volatile_coins) < MAX_COINS or MAX_COINS == 0:
                        volatile_coins[coin] = round(threshold_check, 3)
                        debug_log(
                            f'{coin} has gained {volatile_coins[coin]}% within the last {TIME_DIFFERENCE} minutes, calculating volume in {PAIR_WITH}',
                            False)
                        print(
                            f'{coin} has gained {volatile_coins[coin]}% within the last {TIME_DIFFERENCE} minutes, calculating volume in {PAIR_WITH}')

                    else:
                        debug_log(
                            f'{coin} has gained {round(threshold_check, 3)}% within the last {TIME_DIFFERENCE} minutes, but you are holding max number of coins',
                            False)
                        print(
                            f'{txcolors.WARNING}{coin} has gained {round(threshold_check, 3)}% within the last {TIME_DIFFERENCE} minutes, but you are holding max number of coins{txcolors.DEFAULT}')

        elif threshold_check < CHANGE_IN_PRICE:
            coins_down += 1

        else:
            coins_unchanged += 1

    # Here goes new code for external signalling
    debug_log("Executing external code for external signalling", False)
    externals = external_buy_signals()
    ex_number = 0

    for ex_coin in externals:
        if ex_coin not in volatile_coins and ex_coin not in coins_bought and (
                len(coins_bought) + ex_number + len(volatile_coins)) < MAX_COINS:
            volatile_coins[ex_coin] = 1
            ex_number += 1
            debug_log(f'External BUY signal received on {ex_coin}, calculating volume in {PAIR_WITH}', False)
            print(f'External BUY signal received on {ex_coin}, calculating volume in {PAIR_WITH}')

    return volatile_coins, len(volatile_coins), historical_prices[hsp_head]
