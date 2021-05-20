from src.config import USE_TRAILING_STOP_LOSS, USE_STOCH_RSI
from src.sell import sell_coins_default, sell, sell_all
from src.update_portfolio import update_portfolio
from src.remove_coins import remove_from_portfolio
from src.wait_for_price import wait_for_price_default, wait_for_price
from src.convert_volume import convert_volume
from src.strategies.stoch_rsi import get_rsi_series, rsi, stochrsi, stochrsi_ema, check_rsi_buy_signal, check_rsi_sell_signal
from src.get_price import get_price
from src.buy import buy


def strategy_factory():
    if USE_TRAILING_STOP_LOSS:
        trailing_stop_loss()
    elif USE_STOCH_RSI:
        stoch_rsi()
    else:
        default()


def default():
    coins, last_price = wait_for_price_default(get_price())
    volume, last_price = convert_volume(coins, last_price)
    orders, last_price, volume = buy(volume, last_price)
    update_portfolio(orders, last_price, volume)
    coins_sold = sell_coins_default()
    remove_from_portfolio(coins_sold)


def trailing_stop_loss():
    coins, last_price = wait_for_price_default(get_price())
    volume, last_price = convert_volume(coins, last_price)
    orders, last_price, volume = buy(volume, last_price)
    update_portfolio(orders, last_price, volume)
    coins_sold = sell_coins_default()
    remove_from_portfolio(coins_sold)


def stoch_rsi():
    coins = get_price()
    coins_rsi = get_rsi_series(coins)
    coins_with_buy_signal = check_rsi_buy_signal(coins_rsi)
    coins, last_price = wait_for_price(coins_rsi)
    volume, last_price = convert_volume(coins, last_price)
    orders, last_price, volume = buy(volume, last_price)
    coins_with_sell_signal = check_rsi_sell_signal()
    coins_sold = sell(coins_with_sell_signal)
    remove_from_portfolio(coins_sold)
