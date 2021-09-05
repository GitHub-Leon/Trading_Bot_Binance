from enum import Enum
from bs4 import BeautifulSoup
from helium import *
import json
import os

from src.config import ELON_MIRROR_WEB_URL, DEBUG, TEMP_FILE_PATH, elon_mirror_saved_btc_balance_file
from src.helpers.scripts.logger import debug_log, console_log


class ActionType(Enum):
    NO = 0
    BUY = 1
    SELL = 2


ELON_TEMP_FILE_PATH = TEMP_FILE_PATH + elon_mirror_saved_btc_balance_file


def is_action(ignore_sell):
    debug_log(f'elon_mirror_thread: Test for action.', False)

    current_elon_btc_balance = 0.0
    loaded_elon_btc_balance = 0.0

    # Get data from webpage
    try:
        debug_log(f'elon_mirror_thread: Start firefox headless and wait for page source.', False)
        browser = start_firefox(ELON_MIRROR_WEB_URL, headless=True)  # start headless browser
        html = browser.page_source

        soup = BeautifulSoup(html, features="lxml")
        current_elon_btc_balance = float(soup.find_all("span", {"data-original-title": "Balance"})[0].get_text())
        debug_log(f'elon_mirror_thread: Filtered Elon´s btc balance.', False)

    except Exception as e:
        debug_log(
            f'elon_mirror_thread: Error while web scraping. Exception: {e}', True)
        if DEBUG:
            console_log(f'elon_mirror_thread: Error while web scraping. Exception: {e}')

    # Try to load old btc balance from temp file
    try:
        debug_log(f'elon_mirror_thread: Try to load old btc balance from temp file.', False)

        if not os.path.exists(ELON_TEMP_FILE_PATH):  # check if file exists
            # write new temp file
            f = open(ELON_TEMP_FILE_PATH, "a")
            f.write('{"elon_btc_balance":' + str(current_elon_btc_balance) + '}')
            f.close()

            loaded_elon_btc_balance = current_elon_btc_balance
        else:
            # open and read temp file
            f = open(ELON_TEMP_FILE_PATH, )
            loaded_elon_btc_balance = json.load(f)["elon_btc_balance"]
            f.close()

            # delete temp file
            os.remove(ELON_TEMP_FILE_PATH)

            # write new temp file
            f = open(ELON_TEMP_FILE_PATH, "a")
            f.write('{"elon_btc_balance":' + str(current_elon_btc_balance) + '}')
            f.close()

    except Exception as e:
        debug_log(
            f'elon_mirror_thread: Error while reading/writing temp file. Exception: {e}', True)
        if DEBUG:
            console_log(f'elon_mirror_thread: Error while reading temp file. Exception: {e}')

    elon_balance_diff = current_elon_btc_balance - loaded_elon_btc_balance  # getting diff between new and old balance

    if elon_balance_diff > 0.0:  # It´s a buy action
        return ActionType.BUY, current_elon_btc_balance, elon_balance_diff

    if not ignore_sell and elon_balance_diff < 0.0:  # It´s a sell action
        return ActionType.SELL, current_elon_btc_balance, elon_balance_diff

    return ActionType.NO, current_elon_btc_balance, elon_balance_diff
