# use for environment variables
import os
import sys
import threading
import time

from src.config import BTC_BALANCE, FILL_BALANCE, ELON_MIRROR_RECHECK_INTERVAL, bot_paused, DEBUG
from src.helpers.scripts.logger import debug_log, console_log
from src.strategies.elon_mirror.check_btc_address_website import is_action, ActionType, get_action_type


def analyze():
    ignore_sell = False
    btc_balance = BTC_BALANCE

    u_btc_balance = 10  # TODO: get users btc_balance
    if BTC_BALANCE > u_btc_balance:  # check if user´s owns less btc than the BTC_BALANCE value
        if FILL_BALANCE:  # only ignore sell triggers if the user wants to fill up first own balance
            ignore_sell = True
        btc_balance = u_btc_balance

    if not is_action(ignore_sell):  # exit analyze if there is no action
        return -1, None

    # there is action
    action_type = get_action_type()

    if action_type == ActionType.BUY:  # Buy action triggered
        amount_to_buy = 0

        debug_log(f'elon_mirror_thread: Buy signal triggered.', False)
        if DEBUG:
            console_log(f'elon_mirror_thread: Buy signal triggered.')

        if FILL_BALANCE:  # let´s try to fill up btc_balance
            u_usdt_balance = 100  # TODO: get amount available on user´s account
            btc_price = 100  # TODO: get current btc price
            if ((btc_balance - u_btc_balance) * btc_price) > u_usdt_balance:  # can´t afford that much btc
                debug_log(f'elon_mirror_thread: Not enough usdt to afford {btc_balance - u_btc_balance}.', False)
                if DEBUG:
                    console_log(f'elon_mirror_thread: Not enough usdt to afford {btc_balance - u_btc_balance}.')

                amount_to_buy = u_btc_balance / btc_price  # buy as much btc as we can
            else:  # can afford that much btc
                debug_log(f'elon_mirror_thread: Can afford enough btc to fill up.', False)
                if DEBUG:
                    console_log(f'elon_mirror_thread: Can afford enough btc to fill up.')

                amount_to_buy = btc_balance - u_btc_balance  # fill up balance to BTC_BALANCE

        return amount_to_buy, action_type
    elif action_type == ActionType.SELL:  # Sell action triggered
        amount_to_sell = 0

        debug_log(f'elon_mirror_thread: Sell signal triggered.', False)
        if DEBUG:
            console_log(f'elon_mirror_thread: Sell signal triggered.')

        # TODO: Sell in percentage (btc_balance * (elon_wallet/elon_buy_amount))
        return amount_to_sell, action_type




def do_work():
    while True:
        try:
            if not threading.main_thread().is_alive() or bot_paused:  # kills itself, if the main bot isn't running
                exit()

            debug_log(f'elon_mirror_thread: Analyzing elon´s btc address', False)
            if DEBUG:
                console_log(f'elon_mirror_thread: Analyzing elon´s btc address')

            amount, action_type = analyze()

            if action_type == ActionType.BUY:
                debug_log(
                    f'elon_mirror_thread: Try to buy {amount} btc.',
                    False)
                if DEBUG:
                    console_log(
                        f'elon_mirror_thread: Try to buy {amount} btc.')
                # TODO: buy amount btc

            elif action_type == ActionType.SELL:
                debug_log(
                    f'elon_mirror_thread: Try to sell {amount} btc.',
                    False)
                if DEBUG:
                    console_log(
                        f'elon_mirror_thread: Try to sell {amount} btc.')
                # TODO: sell amount btc

            else:
                debug_log(
                    f'elon_mirror_thread: No action to do.',
                    False)
                if DEBUG:
                    console_log(
                        f'elon_mirror_thread: No action to do.')

        except Exception as e:
            debug_log(f"Error in Module: {sys.argv[0]}. Restarting Module", True)
            if DEBUG:
                console_log(f'Error in Module: {sys.argv[0]}\n Restarting...')

        finally:  # wait, no matter if there's an error or not
            time.sleep((ELON_MIRROR_RECHECK_INTERVAL * 60))
