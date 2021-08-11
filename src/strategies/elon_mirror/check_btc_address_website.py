from enum import Enum
from bs4 import BeautifulSoup
from selenium import webdriver


from src.config import ELON_MIRROR_WEB_URL
from src.helpers.scripts.logger import debug_log, console_log

class ActionType(Enum):
    BUY = 1
    SELL = 2


def is_action(ignore_sell):
    try:
        driver = webdriver.PhantomJS()
        driver.get(ELON_MIRROR_WEB_URL)
        p_element = driver.find_element_by_id(id_='intro-text')

        console_log(driver)
    except Exception as e:
        debug_log(e, False)  # TODO: cloudflare version 2 - no get access
    return True


def get_btc_balance():
    return


def get_action_btc_amount():
    return


def get_action_type():
    return ActionType.BUY
