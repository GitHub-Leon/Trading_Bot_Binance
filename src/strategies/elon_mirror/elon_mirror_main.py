import time

from src.helpers.scripts.logger import debug_log, console_log
from src.config import ELON_MIRROR_RECHECK_INTERVAL, BTC_BALANCE
from src.strategies.elon_mirror.check_btc_address import is_action, get_btc_balance, get_action_btc_amount, \
    get_action_type, ActionType


def only_elon_mirror_strategy():
    """Only elon mirroring is active. Focus on supervising elon ;D"""

    debug_log("Only elon mirror mode is active.", False)
    console_log("Only elon mirror mode is active.")

    if is_action():  # action is going on
        elon_btc_balance = get_btc_balance()
        elon_action_btc_amount = get_action_btc_amount()
        elon_action_type = get_action_type()

        if BTC_BALANCE == 0 and elon_action_type == ActionType.SELL:  # currently no btc and elon sells -> we can´t sell
            return

        action_percentage = elon_action_btc_amount / elon_btc_balance * 100

    time.sleep(ELON_MIRROR_RECHECK_INTERVAL * 60)
    return


def elon_mirror_strategy():
    return
