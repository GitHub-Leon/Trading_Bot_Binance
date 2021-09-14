# This module handles the sell logic of our bot.

import math
import re  # regex
import time
from datetime import datetime

from src.classes.TxColor import txcolors
from src.config import coins_bought, client, TRAILING_TAKE_PROFIT, TRAILING_STOP_LOSS, USE_TRAILING_STOP_LOSS, \
    LOG_TRADES, TEST_MODE, DEBUG, TRADING_FEE, QUANTITY, PAIR_WITH, USE_DEFAULT_STRATEGY, MSG_DISCORD, USE_LIMIT_ORDERS
from src.helpers.decimals import decimals
from src.helpers.scripts import logger
from src.helpers.scripts.balance_report import balance_report
from src.helpers.scripts.discord_msg_trades import msg_discord
from src.strategies.default.get_price import get_price
from src.strategies.external_signals import external_sell_signals
from src.update_globals import update_session_profit, update_volatility_cooloff
from src.threads.thread_manager import start_bnb_auto_buy_thread, start_sell_thread


def sell_coins():
    """Sell coins that have reached the STOP LOSS or TAKE PROFIT threshold."""

    logger.debug_log("Sell coins that have reached the STOP LOSS or TAKE PROFIT threshold", False)
    logger.debug_log("Get last price", False)

    last_prices = get_price(False)  # don't populate rolling window
    coins_sold = {}

    # sell signals of modules
    externals = external_sell_signals()  # gets coins with sell signal provided by modules

    for ex_coin in externals:
        if ex_coin in list(coins_bought):
            logger.debug_log(f'External SELL signal received on {ex_coin}', False)
            logger.console_log(f'External SELL signal received on {ex_coin}')

            coins_sold = coins_to_sell(ex_coin, coins_sold,
                                       last_prices)  # adds coin to coins that have been sold already

    # standard sell signals (TP, SL or bearish market)
    for coin in list(coins_bought):
        if coin not in coins_sold:
            from src.config import hsp_head, sell_bearish  # to update values

            TP = float(coins_bought[coin]['bought_at']) + (
                    float(coins_bought[coin]['bought_at']) * coins_bought[coin]['take_profit']) / 100
            SL = float(coins_bought[coin]['bought_at']) + (
                    float(coins_bought[coin]['bought_at']) * coins_bought[coin]['stop_loss']) / 100

            last_price = float(last_prices[coin]['price'])
            buy_price = float(coins_bought[coin]['bought_at'])
            price_change = float((last_price - buy_price) / buy_price * 100)

            LEVERAGED_TOKEN = re.match(r'.*DOWNUSDT$', coin) or re.match(r'.*UPUSDT$', coin)  # if coin is leveraged

            # check that the price is above the take profit and readjust SL and TP accordingly if trialing stop loss used
            if last_price > TP and USE_TRAILING_STOP_LOSS:
                logger.debug_log(
                    "Price is above the take profit and readjust SL and TP accordingly if trailing stop loss used",
                    False)
                # increasing TP by TRAILING_TAKE_PROFIT (essentially next time to readjust SL)
                logger.debug_log("Increasing TP by TRAILING_TAKE_PROFIT (essentially next time to readjust SL)", False)
                coins_bought[coin]['take_profit'] = coins_bought[coin]['take_profit'] + TRAILING_TAKE_PROFIT
                coins_bought[coin]['stop_loss'] = coins_bought[coin]['stop_loss'] + TRAILING_STOP_LOSS
                logger.debug_log(
                    f"{coin} TP reached, adjusting TP {coins_bought[coin]['take_profit']:.2f} and SL {coins_bought[coin]['stop_loss']:.2f} accordingly to lock-in profit",
                    False)
                if DEBUG:
                    logger.console_log(
                        f"{coin} TP reached, adjusting TP {coins_bought[coin]['take_profit']:.2f} and SL {coins_bought[coin]['stop_loss']:.2f} accordingly to lock-in profit")

            # check that the price is below the stop loss or above take profit (if trailing stop loss not used) and sell if this is the case or when market is bearish
            if (last_price < SL or (
                    last_price > TP and not USE_TRAILING_STOP_LOSS)) and USE_DEFAULT_STRATEGY or sell_bearish:

                # use a limit order to sell the coin
                if USE_LIMIT_ORDERS:
                    # try to create a real order
                    logger.debug_log("Try to create a real order (limit)", False)
                    try:
                        if not TEST_MODE:  # use limit sell when not in TEST_MODE
                            coins_sold = start_sell_thread(coin, coins_sold, last_prices)
                            coins_sold[coin] = coins_bought[coin]  # add coin to coins sold after starting a thread to sell it
                        if TEST_MODE:  # use market sell if TEST_MODE
                            coins_sold = coins_to_sell(coin, coins_sold, last_prices)

                    # error handling here in case position cannot be placed
                    except Exception as e:
                        logger.console_log("error: " + str(e))
                        logger.debug_log(
                            "Error while trying to place a real order. SL/TP or bearish market triggered (Limit). Error-Message: " + str(
                                e), True)

                    else:
                        logger.debug_log("SL/TP or bearish market triggered (Limit).", False)

                if not USE_LIMIT_ORDERS:
                    # try to create a real order
                    logger.debug_log("Try to create a real order", False)
                    try:
                        coins_sold = coins_to_sell(coin, coins_sold, last_prices)

                    # error handling here in case position cannot be placed
                    except Exception as e:
                        logger.console_log("error: " + str(e))
                        logger.debug_log(
                            "Error while trying to place a real order. SL/TP or bearish market triggered. Error-Message: " + str(
                                e), True)

                    else:
                        logger.debug_log("SL/TP or bearish market triggered.", False)

            # no action; print once every TIME_DIFFERENCE
            if hsp_head == 1:
                if len(coins_bought) > 0 and coin not in coins_sold:
                    logger.debug_log(
                        f'Not selling {coin} for now {buy_price} - {last_price}: {price_change - (TRADING_FEE * 2):.2f}% Est: {(QUANTITY * (price_change - (TRADING_FEE * 2))) / 100:.2f}$',
                        False)
                    logger.console_log(
                        f'Not selling {coin} for now {buy_price} - {last_price}: {txcolors.SELL_PROFIT if price_change - (TRADING_FEE * 2) >= 0. else txcolors.SELL_LOSS}{price_change - (TRADING_FEE * 2):.2f}%{txcolors.DEFAULT} Est: {txcolors.SELL_PROFIT if price_change - (TRADING_FEE * 2) >= 0. else txcolors.SELL_LOSS}{(QUANTITY * (price_change - (TRADING_FEE * 2))) / 100:.{decimals()}f} {PAIR_WITH}{txcolors.DEFAULT}')

    return coins_sold


def coins_to_sell(coin, coins_sold, last_prices):
    last_price = float(last_prices[coin]['price'])
    buy_price = float(coins_bought[coin]['bought_at'])
    price_change = float((last_price - buy_price) / buy_price * 100)

    # try to create a real order
    logger.debug_log("Try to create a real order", False)
    try:
        if not TEST_MODE:
            sell_coins_limit = client.create_order(
                symbol=coin,
                side='SELL',
                type='MARKET',
                quantity=coins_bought[coin]['volume']

            )

    # error handling here in case position cannot be placed
    except Exception as e:
        logger.debug_log("Error while trying to place a real order (coins_to_sell). Error-Message: " + str(e), True)

    # run the else block if coin has been sold and create a dict for each coin sold
    else:
        logger.debug_log("The coin has been sold", False)

        from src.update_globals import update_profitable_trades, update_losing_trades, update_session_fees
        if price_change - (TRADING_FEE * 2) < 0:
            update_losing_trades()  # coin was not profitable
            logger.debug_log(
                f"Sell signal received, selling {coins_bought[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%",
                False)
            logger.console_log(
                f"{txcolors.SELL_LOSS}Sell signal received, selling {coins_bought[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%{txcolors.DEFAULT}")
        elif price_change - (TRADING_FEE * 2) >= 0:
            update_profitable_trades()  # coin was profitable
            logger.debug_log(
                f"Sell signal received, selling {coins_bought[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%",
                False)
            logger.console_log(
                f"{txcolors.SELL_PROFIT}Sell signal received, selling {coins_bought[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%{txcolors.DEFAULT}")

        coins_sold[coin] = coins_bought[coin]

        # prevent system from buying this coin for the next TIME_DIFFERENCE minutes
        update_volatility_cooloff(coin, datetime.now())

        update_session_profit(price_change - (TRADING_FEE * 2))
        update_session_fees(QUANTITY * (1 + price_change / 100) * TRADING_FEE / 100)
        logger.profit_log(price_change - (TRADING_FEE * 2))

        # Log trade
        if LOG_TRADES or MSG_DISCORD:
            profit = ((last_price - buy_price) * coins_sold[coin]['volume']) * (
                    1 - (TRADING_FEE * 2))  # adjust for trading fee here

            if LOG_TRADES:
                logger.trade_log(
                    f"Sell: {coins_sold[coin]['volume']} {coin} - {buy_price} - {last_price} Profit: {profit:.{decimals()}f} {price_change - (TRADING_FEE * 2):.2f}%")
            if MSG_DISCORD:
                msg_discord(
                    f"```Sell: {coin}\nEntry: {buy_price}\nClose: {last_price}\nProfit: {price_change - (TRADING_FEE * 2):.2f}%```")

        # print balance report
        balance_report(coins_sold)

    # check for bnb
    start_bnb_auto_buy_thread()

    return coins_sold


def round_decimals_down(number: float, decimal_places: int = 2):  # NOT USED AS OF RIGHT NOW!!!
    """
    Returns a value rounded down to a specific number of decimal places.
    """
    if decimal_places == 0:
        return math.floor(number)

    factor = 10 ** decimal_places
    return math.floor(number * factor) / factor
