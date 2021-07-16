import src.config as config
from src.helpers.scripts.logger import debug_log


def update_session_profit(session_profit):
    debug_log("Update session profit", False)
    config.session_profit += session_profit


def update_historical_prices(prices, hsp_head):
    debug_log("Update historical prices", False)
    config.historical_prices[hsp_head] = prices


def update_hsp_head(hsp_head):
    debug_log("Update hsp head", False)
    config.hsp_head = hsp_head


def update_volatility_cooloff(coin, time):
    debug_log("Update volatility cooloff", False)
    config.volatility_cooloff[coin] = time


def update_bot_paused(bot_paused):
    debug_log("Update bot paused", False)
    config.bot_paused = bot_paused


def set_default_values():
    debug_log("Set all values to default", False)
    config.session_profit = 0


def update_sell_bearish(sell_bearish):
    debug_log("Update sell_bearish", False)
    config.sell_bearish = sell_bearish
