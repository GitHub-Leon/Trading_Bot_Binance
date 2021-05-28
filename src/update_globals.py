import src.config as config


def update_session_profit(session_profit):
    config.session_profit += session_profit


def update_historical_prices(prices, hsp_head):
    config.historical_prices[hsp_head] = prices


def update_hsp_head(hsp_head):
    config.hsp_head = hsp_head


def update_volatility_cooloff(coin, time):
    config.volatility_cooloff[coin] = time


def update_bot_paused(bot_paused):
    config.bot_paused = bot_paused

