# use for environment variables
import os
import sys
import threading
import time

from tradingview_ta import TA_Handler, Interval

from src.config import BTC_BALANCE, FILL_BALANCE, ELON_MIRROR_RECHECK_INTERVAL, bot_paused, DEBUG
from src.helpers.scripts.logger import debug_log, console_log
from src.strategies.elon_mirror.check_btc_address import isAction, ActionType, get_action_type


def analyze():
    ignore_sell = False
    # TODO: get users btc_balance
    u_btc_balance = 10
    if BTC_BALANCE > u_btc_balance:  # check if user´s owns less btc than the BTC_BALANCE value
        if FILL_BALANCE:  # only ignore sell triggers if the user wants to fill up first own balance
            ignore_sell = True

    if not isAction(ignore_sell):  # exit analyze if there is no action
        return

    # there is action
    action_type = get_action_type()

    if action_type == ActionType.BUY:  # Buy action triggered
        debug_log(f'elon_mirror_thread: Buy signal triggered.', False)
        if DEBUG:
            console_log(f'elon_mirror_thread: Buy signal triggered.')

        fill_balance_failed = False
        if FILL_BALANCE:  # let´s try to fill up btc_balance
            u_usdt_balance = 100  # TODO: get amount available on user´s account
            btc_price = 100  # TODO: get current btc price
            if ((BTC_BALANCE - u_btc_balance) * btc_price) > u_usdt_balance:  # can´t afford that much btc
                debug_log(f'elon_mirror_thread: Not enough usdt to afford {BTC_BALANCE - u_btc_balance}.', False)
                if DEBUG:
                    console_log(f'elon_mirror_thread: Not enough usdt to afford {BTC_BALANCE - u_btc_balance}.')
                fill_balance_failed = True
            else:  # can afford that much btc
                btc_buy_amount = BTC_BALANCE - u_btc_balance
                # TODO: Try to place order

        if not fill_balance_failed:  # fill balance was successful. end this buy action
            debug_log(f'elon_mirror_thread: Fill_Balance was successful.', False)
            if DEBUG:
                console_log(f'elon_mirror_thread: Fill_Balance was successful.')
            return

        # TODO: buy btc (u_btc_balance * (elon_wallet/elon_buy_amount))

    elif action_type == ActionType.SELL:  # Sell action triggered
        # TODO: Check if we have as much btc as told in BTC_BALANCE
        # TODO: Sell in percentage (BTC_BALANCE * (elon_wallet/elon_buy_amount))
        return
    return


def do_work():
    while True:
        try:
            if not threading.main_thread().is_alive() or bot_paused:  # kills itself, if the main bot isn't running
                exit()

            debug_log(f'elon_mirror_thread: Analyzing elon´s btc address', False)
            if DEBUG:
                console_log(f'elon_mirror_thread: Analyzing elon´s btc address')

            analyze()

            debug_log(
                f'elon_mirror_thread: ',
                False)
            if DEBUG:
                console_log(
                    f'elon_mirror_thread: ')

        except Exception as e:
            debug_log(f"Error in Module: {sys.argv[0]}. Restarting Module", True)
            if DEBUG:
                console_log(f'Error in Module: {sys.argv[0]}\n Restarting...')

        finally:  # wait, no matter if there's an error or not
            time.sleep((ELON_MIRROR_RECHECK_INTERVAL * 60))
