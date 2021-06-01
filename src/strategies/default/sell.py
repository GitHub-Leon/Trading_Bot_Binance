# This module handles the sell logic of our bot.

from datetime import datetime

# local dependencies
from src.classes.TxColor import txcolors
from src.config import coins_bought, client, TRAILING_TAKE_PROFIT, TRAILING_STOP_LOSS, USE_TRAILING_STOP_LOSS, \
    LOG_TRADES, TEST_MODE, DEBUG, TRADING_FEE, QUANTITY, PAIR_WITH
from src.helpers.decimals import decimals
from src.helpers.scripts import logger
from src.helpers.scripts.balance_report import balance_report
from src.strategies.default.get_price import get_price
from src.update_globals import update_session_profit, update_volatility_cooloff


def sell_coins():
    logger.debug_log("Sell coins that have reached the STOP LOSS or TAKE PROFIT threshold", False)
    """Sell coins that have reached the STOP LOSS or TAKE PROFIT threshold."""

    logger.debug_log("Get last price", False)
    last_prices = get_price(False)  # don't populate rolling window
    coins_sold = {}

    for coin in list(coins_bought):
        from src.config import hsp_head  # to update values

        TP = float(coins_bought[coin]['bought_at']) + (
                float(coins_bought[coin]['bought_at']) * coins_bought[coin]['take_profit']) / 100
        SL = float(coins_bought[coin]['bought_at']) + (
                float(coins_bought[coin]['bought_at']) * coins_bought[coin]['stop_loss']) / 100

        last_price = float(last_prices[coin]['price'])
        buy_price = float(coins_bought[coin]['bought_at'])
        price_change = float((last_price - buy_price) / buy_price * 100)

        # check that the price is above the take profit and readjust SL and TP accordingly if trialing stop loss used
        if last_price > TP and USE_TRAILING_STOP_LOSS:
            logger.debug_log(
                "Price is above the take profit and readjust SL and TP accordingly if trailing stop loss used", False)
            # increasing TP by TRAILING_TAKE_PROFIT (essentially next time to readjust SL)
            logger.debug_log("Increasing TP by TRAILING_TAKE_PROFIT (essentially next time to readjust SL)", False)
            coins_bought[coin]['take_profit'] = price_change + TRAILING_TAKE_PROFIT
            coins_bought[coin]['stop_loss'] = coins_bought[coin]['take_profit'] - TRAILING_STOP_LOSS

            logger.debug_log(
                f"{coin} TP reached, adjusting TP {coins_bought[coin]['take_profit']:.2f} and SL {coins_bought[coin]['stop_loss']:.2f} accordingly to lock-in profit",
                False)
            if DEBUG:
                print(
                    f"{coin} TP reached, adjusting TP {coins_bought[coin]['take_profit']:.2f} and SL {coins_bought[coin]['stop_loss']:.2f} accordingly to lock-in profit")

            continue

        # check that the price is below the stop loss or above take profit (if trailing stop loss not used) and sell if this is the case
        if last_price < SL or (last_price > TP and not USE_TRAILING_STOP_LOSS):
            logger.debug_log(
                "The price is below the stop loss or above take profit (if trailing stop loss not used) and sell if this is the case",
                False)
            if price_change - (TRADING_FEE * 2) < 0:
                logger.debug_log(
                    f"{txcolors.SELL_LOSS}TP or SL reached, selling {coins_bought[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%{txcolors.DEFAULT}",
                    False)
                print(
                    f"{txcolors.SELL_LOSS}TP or SL reached, selling {coins_bought[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%{txcolors.DEFAULT}")
            elif price_change - (TRADING_FEE * 2) >= 0:
                logger.debug_log(
                    f"{txcolors.SELL_PROFIT}TP or SL reached, selling {coins_bought[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%{txcolors.DEFAULT}",
                    False)
                print(
                    f"{txcolors.SELL_PROFIT}TP or SL reached, selling {coins_bought[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%{txcolors.DEFAULT}")

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
                logger.debug_log("Error while trying to place a real order. Error-Message: " + str(e), True)

            # run the else block if coin has been sold and create a dict for each coin sold
            else:
                logger.debug_log("The coin has been sold", False)
                coins_sold[coin] = coins_bought[coin]

                # prevent system from buying this coin for the next TIME_DIFFERENCE minutes
                update_volatility_cooloff(coin, datetime.now())

                # Log trade
                if LOG_TRADES:
                    profit = ((last_price - buy_price) * coins_sold[coin]['volume']) * (
                            1 - (TRADING_FEE * 2))  # adjust for trading fee here
                    logger.trade_log(
                        f"Sell: {coins_sold[coin]['volume']} {coin} - {buy_price} - {last_price} Profit: {profit:.{decimals()}f} {price_change - (TRADING_FEE * 2):.2f}%")
                    update_session_profit(price_change - (TRADING_FEE * 2))

                # print balance report
                balance_report()
            continue

            # no action; print once every TIME_DIFFERENCE
        if hsp_head == 1:
            if len(coins_bought) > 0:
                logger.debug_log(
                    f'TP or SL not yet reached, not selling {coin} for now {buy_price} - {last_price}: {price_change - (TRADING_FEE * 2):.2f}% Est: {(QUANTITY * (price_change - (TRADING_FEE * 2))) / 100:.2f}$',
                    False)
                print(
                    f'TP or SL not yet reached, not selling {coin} for now {buy_price} - {last_price}: {txcolors.SELL_PROFIT if price_change - (TRADING_FEE * 2) >= 0. else txcolors.SELL_LOSS}{price_change - (TRADING_FEE * 2):.2f}%{txcolors.DEFAULT} Est: {txcolors.SELL_PROFIT if price_change - (TRADING_FEE * 2) >= 0. else txcolors.SELL_LOSS}{(QUANTITY * (price_change - (TRADING_FEE * 2))) / 100:.{decimals()}f} {PAIR_WITH}{txcolors.DEFAULT}')

        if hsp_head == 1 and len(coins_bought) == 0:
            logger.debug_log("Not holding any coins", False)
            print(f'Not holding any coins')

    return coins_sold
