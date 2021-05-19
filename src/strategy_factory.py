from src.config import USE_TRAILING_STOP_LOSS, USE_STOCH_RSI
from src.sell import sell_coins
from src.update_portfolio import update_portfolio
from src.remove_coins import remove_from_portfolio
from src.wait_for_price import wait_for_price
from src.convert_volume import convert_volume
from src.trade import buy


def strategy_factory():
    if USE_TRAILING_STOP_LOSS:
        trailing_stop_loss()
    elif USE_STOCH_RSI:
        stoch_rsi()
    else:
        default()


def default():
    coins, last_price = wait_for_price()
    volume, last_price = convert_volume(coins, last_price)
    orders, last_price, volume = buy(volume, last_price)
    update_portfolio(orders, last_price, volume)
    coins_sold = sell_coins()
    remove_from_portfolio(coins_sold)


def trailing_stop_loss():
    coins, last_price = wait_for_price()
    volume, last_price = convert_volume(coins, last_price)
    orders, last_price, volume = buy(volume, last_price)
    update_portfolio(orders, last_price, volume)
    coins_sold = sell_coins()
    remove_from_portfolio(coins_sold)


def stoch_rsi():
    pass