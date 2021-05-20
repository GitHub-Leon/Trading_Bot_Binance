# This module calculated price differences and executes the sell_coins function once a threshold is reached

import time
from datetime import datetime, timedelta

# local dependencies
from src.config import PAIR_WITH, TIME_DIFFERENCE, RECHECK_INTERVAL, CHANGE_IN_PRICE, coins_bought, MAX_COINS, USE_DEFAULT_STRATEGY, USE_TRAILING_STOP_LOSS, USE_STOCH_RSI
from src.get_price import get_price
from src.strategies.stoch_rsi import get_rsi_series, check_rsi_sell_signal
from src.remove_coins import remove_from_portfolio
from src.sell import sell_coins_default, sell
from src.colors import txcolors


def wait_for_price_default(initial_prices):
    """calls the initial price and ensures the correct amount of time has passed
    before reading the current price again"""

    coins = {}

    while initial_prices['BNB' + PAIR_WITH]['time'] > datetime.now() - timedelta(seconds=TIME_DIFFERENCE):
        i = 0
        if USE_DEFAULT_STRATEGY or USE_TRAILING_STOP_LOSS:
            while i < RECHECK_INTERVAL:
                coins_sold = sell_coins_default()
                remove_from_portfolio(coins_sold)
                time.sleep((TIME_DIFFERENCE / RECHECK_INTERVAL))
                i += 1

    else:
        last_prices = get_price()
        info_change = -100.00
        info_coin = 'none'
        info_start = 0.00
        info_stop = 0.00

    # calculate the difference between the first and last price reads
    for coin in initial_prices:
        last_price = float(last_prices[coin]['price'])
        initial_price = float(initial_prices[coin]['price'])

        threshold_check = (last_price - initial_price) / initial_price * 100

        if threshold_check > info_change:
            info_change = threshold_check
            info_coin = coin
            info_start = initial_price
            info_stop = last_price

        # each coin with higher gains than our CHANGE_IN_PRICE is added to the volatile_coins dict if less than MAX_COINS is not reached.
        if threshold_check > CHANGE_IN_PRICE:
            if len(coins_bought) + len(coins) < MAX_COINS or MAX_COINS == 0:
                coins[coin] = threshold_check
                coins[coin] = round(coins[coin], 3)
                print(
                    f'{coin} has gained {coins[coin]}% in the last {TIME_DIFFERENCE} seconds, calculating volume in {PAIR_WITH}')

            else:
                print(
                    f'{txcolors.WARNING}{coin} has gained {threshold_check}% in the last {TIME_DIFFERENCE} seconds, but you are holding max number of coins{txcolors.DEFAULT}')

    # Print more info if there are no volatile coins this iteration
    if info_change < CHANGE_IN_PRICE:
        print(f'No coins moved more than {CHANGE_IN_PRICE}% in the last {TIME_DIFFERENCE} second(s)')

    print(
        f'Max movement {float(info_change):.2f}% by {info_coin} from {float(info_start):.4f} to {float(info_stop):.4f}')

    return coins, last_prices


def wait_for_price(initial_prices):

    coins = {}

    while initial_prices['BNB' + PAIR_WITH]['time'] > datetime.now() - timedelta(seconds=TIME_DIFFERENCE):
        i = 0
        while i < RECHECK_INTERVAL:
            coins_with_sell_signal = check_rsi_sell_signal()
            coins_sold = sell(coins_with_sell_signal)
            remove_from_portfolio(coins_sold)
            time.sleep((TIME_DIFFERENCE / RECHECK_INTERVAL))
            i += 1

    else:
        last_prices = get_price()
        info_change = -100.00
        info_coin = 'none'
        info_start = 0.00
        info_stop = 0.00

    for coin in initial_prices:
        last_price = float(last_prices[coin]['price'])
        initial_price = float(initial_prices[coin]['price'])

    return coins, last_prices
