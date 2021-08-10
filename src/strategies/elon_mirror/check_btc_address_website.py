from enum import Enum
from bs4 import BeautifulSoup
import cloudscraper


from src.config import ELON_MIRROR_WEB_URL
from src.helpers.scripts.logger import debug_log

class ActionType(Enum):
    BUY = 1
    SELL = 2


def is_action(ignore_sell):
    try:
        scraper = cloudscraper.create_scraper()
        html = scraper.get(ELON_MIRROR_WEB_URL).text
    except Exception as e:
        debug_log(e, False)  # TODO: cloudflare version 2 - no get access
    return True


def get_btc_balance():
    return


def get_action_btc_amount():
    return


def get_action_type():
    return ActionType.BUY
