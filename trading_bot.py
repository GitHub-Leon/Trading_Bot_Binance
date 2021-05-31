# The main modules that executes the script repeatedly

# local dependencies
from src.config import bot_wait
from src.helpers.scripts.sell_all_coins import sell_all
from src.remove_coins import remove_from_portfolio
from src.strategies.default.get_price import get_price
from src.strategies.default.sell import sell_coins
from src.strategies.default.trade import buy
from src.strategies.trading_view.signals import load_signals
from src.update_portfolio import update_portfolio
from src.console.input.console_input import console_input
from src.console.login import login
from src.console.output.before_start import print_before_start
from src.console.input import processing_input
from src.helpers.scripts.logger import debug_log


def main():
    bot_wait()  # waits a specified amount of seconds before starting the bot as a safety measure
    load_signals()  # loads signals into bot
    get_price()  # seed initial prices
    while True:
        orders, last_price, volume = buy()
        update_portfolio(orders, last_price, volume)
        coins_sold = sell_coins()
        remove_from_portfolio(coins_sold)


def startup():
    try:
        debug_log("Start the bot", False)
        main()
    except KeyboardInterrupt:
        debug_log("Exit the bot", False)
        sell_all()


if __name__ == '__main__':
    debug_log("------------------------- START -------------------------", False)
    if login():  # verifies correct login data before starting the bot
        print_before_start()  # before commands can be used
        while True:
            command = console_input()
            processing_input.input_check(command)
