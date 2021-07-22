import sys
import threading
import time

import requests

from src.config import DEBUG, MSG_DISCORD, DISCORD_WEBHOOK_BALANCE, \
    PAIR_WITH, QUANTITY, MAX_COINS
from src.helpers.decimals import decimals
from src.helpers.scripts.logger import debug_log, console_log

# local var
wait_time = 1  # print balance every x hour


def discord_msg_balance():
    """Send a discord push message to a channel every x hours with a balance update"""
    debug_log("Push message to discord channel (balance)", False)

    from src.config import session_profit  # update value

    try:
        INVESTMENT_TOTAL = (QUANTITY * MAX_COINS)
        TOTAL_GAINS = ((QUANTITY * session_profit) / 100)
        INVESTMENT_GAIN = (TOTAL_GAINS / INVESTMENT_TOTAL) * 100

        msg = f"```Total Investment: {INVESTMENT_TOTAL:.{decimals()}f} {PAIR_WITH}\nProfit: {session_profit:.2f}% ({INVESTMENT_GAIN:.2f}%)\nProfit abs.: {TOTAL_GAINS:.{decimals()}f}{PAIR_WITH}```"
        message = msg + "\n\n"

        if MSG_DISCORD:
            mUrl = DISCORD_WEBHOOK_BALANCE
            data = {"content": message}
            response = requests.post(mUrl, json=data)
    except Exception:
        debug_log("Error in discord messaging (balance)", True)

    return


def do_work():
    while True:
        try:
            if not threading.main_thread().is_alive():
                exit()

            discord_msg_balance()
            time.sleep(wait_time * 3600)

        except Exception as e:
            debug_log(f"Error in Module: {sys.argv[0]}. Restarting Module", True)
            if DEBUG:
                console_log(f'Error in Module: {sys.argv[0]}\n Restarting...')

        finally:  # wait, no matter if there's an error or not
            time.sleep(1)
