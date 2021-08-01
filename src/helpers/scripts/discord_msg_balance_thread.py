import sys
import threading
import time
import datetime

import requests

from src.config import DEBUG, MSG_DISCORD, DISCORD_WEBHOOK_BALANCE, MAX_COINS
from src.helpers.decimals import decimals
from src.helpers.scripts.logger import debug_log, console_log

# local var
wait_time = 1  # print balance every x hour


def discord_msg_balance():
    """Send a discord push message to a channel every x hours with a balance update"""
    debug_log("Push message to discord channel (balance)", False)

    # import updated globals
    from src.config import profitable_trades, losing_trades, coins_bought, session_duration, session_profit, QUANTITY, \
        PAIR_WITH, session_fees

    hours, rem = divmod(time.time() - session_duration, 3600)
    minutes, seconds = divmod(rem, 60)

    INVESTMENT_TOTAL = (QUANTITY * MAX_COINS)
    TOTAL_GAINS = ((QUANTITY * session_profit) / 100)
    INVESTMENT_GAIN = (TOTAL_GAINS / INVESTMENT_TOTAL) * 100

    session_duration_msg = "Session duration: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
    fees_spent_msg = "Fees spent approximately: {:.2f} {}".format(session_fees, PAIR_WITH)
    msg = f"```Win/Loss: {profitable_trades}/{losing_trades} \nProfit: {session_profit:.2f}% ({INVESTMENT_GAIN:.2f}%)\nProfit abs.: {TOTAL_GAINS:.{decimals()}f}{PAIR_WITH}\nTrading Volume approximately: {QUANTITY * (losing_trades + profitable_trades + len(coins_bought))} {PAIR_WITH}\n{fees_spent_msg}\n{session_duration_msg}``` "
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
