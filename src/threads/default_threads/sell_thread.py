import time
import sys
import binance.helpers
from datetime import datetime

from src.classes.TxColor import txcolors
from src.config import coins_bought, client, LOG_TRADES, TRADING_FEE, QUANTITY, PAIR_WITH, MSG_DISCORD, DEBUG
from src.helpers.decimals import decimals
from src.helpers.scripts import logger
from src.helpers.scripts.balance_report import balance_report
from src.helpers.scripts.discord_msg_trades import msg_discord
from src.update_globals import update_session_profit
from src.threads.thread_manager import start_bnb_auto_buy_thread
from src.helpers.scripts.logger import debug_log, console_log


def use_limit_sell_order(coin, coins_sold, last_prices):
    coins_bought_new = coins_bought.copy()  # create copy to prevent overwriting
    logger.debug_log("Trying to create limit sell order", False)
    """
    Input coin gets sold via current market price with limit orders
    Returns the updated coins_sold
    """

    logger.debug_log(f"Sell signal for {coin} received", False)
    last_price = float(last_prices[coin]['price'])
    buy_price = float(coins_bought_new[coin]['bought_at'])
    price_change = float((last_price - buy_price) / buy_price * 100)

    while True:
        last_price = float(client.get_symbol_ticker(symbol=coin)['price'])
        buy_price = float(coins_bought_new[coin]['bought_at'])
        price_change = float((last_price - buy_price) / buy_price * 100)

        orders = {}

        try:
            if float(client.get_asset_balance(asset=str(coin).split(PAIR_WITH)[0])['free']) == 0 and float(
                    client.get_asset_balance(asset=str(coin).split(PAIR_WITH)[0])[
                        'locked']) == 0:  # if balance == 0, remove from portfolio

                # in case a buy order is still up, cancel it
                if len(client.get_open_orders(symbol=coin)) > 0:
                    orders[coin] = client.get_open_orders(symbol=coin)
                    while not orders[coin]:
                        time.sleep(1)
                        orders[coin] = client.get_open_orders(symbol=coin)
                    result = client.cancel_order(
                        symbol=coin,
                        orderId=orders[coin][0]['orderId']
                    )

                update_session_fees((QUANTITY*TRADING_FEE/100) * -1)  # subtract already added trading fee from "buying"
                coins_sold[coin] = coins_bought[coin]

                return coins_sold

            # if one sell order is already up (below MIN_NOTATIONAL) and a new buy order bought some
            elif float(client.get_asset_balance(asset=str(coin).split(PAIR_WITH)[0])['locked']) != 0 and float(
                    client.get_asset_balance(asset=str(coin).split(PAIR_WITH)[0])['free']) != 0:
                orders[coin] = client.get_open_orders(symbol=coin)

                while not orders[coin]:
                    time.sleep(1)
                    orders[coin] = client.get_open_orders(symbol=coin)

                result = client.cancel_order(  # old partially filled sell order below MIN_NOTATIONAL
                    symbol=coin,
                    orderId=orders[coin][0]['orderId']
                )
                result = client.cancel_order(  # new partially filled buy order
                    symbol=coin,
                    orderId=orders[coin][1]['orderId']
                )

            elif float(client.get_asset_balance(asset=str(coin).split(PAIR_WITH)[0])[
                           'locked']) != 0:  # if there's already a part locked, cancel the order
                orders[coin] = client.get_open_orders(symbol=coin)

                while not orders[coin]:
                    time.sleep(1)
                    orders[coin] = client.get_open_orders(symbol=coin)

                if float(client.get_asset_balance(asset=str(coin).split(PAIR_WITH)[0])[
                             'locked']) * last_price > 15:  # if less than MIN_NOTATIONAL is available (15$ for binance)
                    result = client.cancel_order(
                        symbol=coin,
                        orderId=orders[coin][0]['orderId']
                    )

                    # Fix step size issue
                    info = client.get_symbol_info('BNBUSDT')
                    step_size = info['filters'][2]['stepSize']
                    quantity = binance.helpers.round_step_size(
                        float(client.get_asset_balance(asset=str(coin).split(PAIR_WITH)[0])['free']), float(step_size))

                    order = client.order_limit_sell(
                        symbol=coin,
                        quantity=quantity,
                        price=last_price
                    )

            elif float(client.get_asset_balance(asset=str(coin).split(PAIR_WITH)[0])[
                           'free']) != 0:  # if a part already got filled
                if len(client.get_open_orders(symbol=coin)) > 0:
                    orders[coin] = client.get_open_orders(symbol=coin)

                    while not orders[coin]:
                        time.sleep(1)
                        orders[coin] = client.get_open_orders(symbol=coin)

                    result = client.cancel_order(
                        symbol=coin,
                        orderId=orders[coin][0]['orderId']
                    )

                order = client.order_limit_sell(
                    symbol=coin,
                    quantity=client.get_asset_balance(asset=str(coin).split(PAIR_WITH)[0])['free'],
                    price=last_price
                )

        except Exception as e:
            logger.debug_log("Error while creating an limit sell order: " + str(e), True)
        else:
            time.sleep(1)  # wait to see if order got filled or not
            try:
                if len(client.get_open_orders(symbol=coin)) == 0:
                    coins_sold[coin] = coins_bought_new[coin]  # add the coin to the sold coins, if no order is open anymore

                    logger.debug_log("Selling coin with limit sell", False)
                    from src.update_globals import update_profitable_trades, update_losing_trades, update_session_fees, \
                        update_volatility_cooloff
                    if price_change - (TRADING_FEE * 2) < 0:
                        update_losing_trades()  # coin was not profitable
                        logger.debug_log(
                            f"Selling {coins_bought_new[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%",
                            False)
                        logger.console_log(
                            f"{txcolors.SELL_LOSS}Selling {coins_bought_new[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%{txcolors.DEFAULT}")
                    elif price_change - (TRADING_FEE * 2) >= 0:
                        update_profitable_trades()  # coin was profitable
                        logger.debug_log(
                            f"Selling {coins_bought_new[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%",
                            False)
                        logger.console_log(
                            f"{txcolors.SELL_PROFIT}Selling {coins_bought_new[coin]['volume']} {coin} - {buy_price} -> {last_price}: {price_change - (TRADING_FEE * 2):.2f}%{txcolors.DEFAULT}")

                    # prevent system from buying this coin for the next TIME_DIFFERENCE minutes
                    update_volatility_cooloff(coin, datetime.now())

                    # update global vars
                    update_session_profit(price_change - (TRADING_FEE * 2))
                    update_session_fees(QUANTITY * (1 + price_change / 100) * TRADING_FEE / 100)

                    # log profits
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

            except Exception as e:
                logger.debug_log("Error while cancelling a limit sell order: " + str(e), True)


def do_work(coin, coins_sold, last_prices):
    try:
        debug_log(f"Trying to sell coin.", False)
        if DEBUG:
            console_log(f'Trying to sell coin.')

        use_limit_sell_order(coin, coins_sold, last_prices)

    except Exception as e:
        debug_log(f"Error in Module: {sys.argv[0]}. Couldn't cancel a limit sell order.", True)
        if DEBUG:
            console_log(f"Error in Module: {sys.argv[0]}\n. Couldn't cancel a limit sell order.")
