import datetime
import sys
import threading
import time

import requests

from src.config import DEBUG, MSG_DISCORD, DISCORD_WEBHOOK_BALANCE, MAX_COINS, TEST_MODE, QUANTITY
from src.helpers.scripts.binance_wallet_balance import total_amount_usdt
from src.helpers.decimals import decimals
from src.helpers.scripts.logger import debug_log, console_log

# local var
wait_time = 1  # print balance every x hour

INVESTMENT = MAX_COINS*QUANTITY
if not TEST_MODE:  # If not testmode, set the starting investment to the current wallet balance
    INVESTMENT = total_amount_usdt()


def discord_msg_balance():
    """Send a discord push message to a channel every x hours with a balance update"""
    debug_log("Push message to discord channel (balance)", False)

    # import updated globals
    from src.config import profitable_trades, losing_trades, coins_bought, session_duration, session_profit, QUANTITY, \
        PAIR_WITH, session_fees

    days, rem = divmod(time.time() - session_duration, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    TOTAL_GAINS = ((QUANTITY * session_profit) / 100)
    INVESTMENT_GAIN = (TOTAL_GAINS / INVESTMENT) * 100
    CURRENT_BALANCE = INVESTMENT + TOTAL_GAINS

    if not TEST_MODE:  # get wallet balance in live mode
        CURRENT_BALANCE = total_amount_usdt()

    session_duration_msg = "Session duration: {:0>1}:{:0>2}:{:0>2}:{:05.2f}".format(int(days), int(hours), int(minutes), seconds)
    fees_spent_msg = "Fees spent approximately: {:.2f} {}\n".format(session_fees, PAIR_WITH)
    trade_win_ration_msg = f"Win/Loss: {profitable_trades}/{losing_trades} \n"
    balance_msg = f"Current balance: {CURRENT_BALANCE:.{decimals()}f} USDT\n"
    percent_profit_msg = f"ROI: {INVESTMENT_GAIN:.2f}%\n"
    profit_abs = f"Profit abs.: {TOTAL_GAINS:.{decimals()}f} {PAIR_WITH}\n"
    trading_volume_msg = f"Trading Volume approximately: {QUANTITY * (losing_trades + profitable_trades + len(coins_bought))} {PAIR_WITH}\n"

    if profitable_trades + losing_trades > 0:  # set a new msg after one trade, to prevent division by zero
        trade_win_ration_msg = f"Win/Loss: {profitable_trades}/{losing_trades} ({(profitable_trades / (losing_trades + profitable_trades) * 100):.2f} %)\n"

    msg = f"```{trade_win_ration_msg}{percent_profit_msg}{profit_abs}{balance_msg}{trading_volume_msg}{fees_spent_msg}{session_duration_msg}``` "
    message = msg + "\n\n"

    if MSG_DISCORD:
        mUrl = DISCORD_WEBHOOK_BALANCE
        data = {"content": message}
        response = requests.post(mUrl, json=data)

    return


def do_work():
    while True:
        try:
            if not threading.main_thread().is_alive():
                exit()

            if datetime.datetime.now().minute == 0:
                discord_msg_balance()
                time.sleep(61)  # sleep 61 secs to prevent it from triggering again

        except Exception as e:
            debug_log(f"Error in Module: {sys.argv[0]}. Restarting Module", True)
            if DEBUG:
                console_log(f'Error in Module: {sys.argv[0]}\n Restarting...')

        finally:  # wait, no matter if there's an error or not
            time.sleep(1)
