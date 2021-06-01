# The main modules that executes the script repeatedly
import sys
import time

# local dependencies
from src.classes.StampedOut import StampedOut
from src.classes.TxColor import txcolors
from src.config import bot_wait
from src.console.input import processing_input
from src.console.input.console_input import console_input
from src.console.login import login
from src.console.output.before_start import print_before_start
from src.helpers.scripts.logger import debug_log
from src.helpers.scripts.sell_all_coins import sell_all
from src.remove_coins import remove_from_portfolio
from src.strategies.default.get_price import get_price
from src.strategies.default.sell import sell_coins
from src.strategies.default.trade import buy
from src.strategies.trading_view.signals import load_signals
from src.update_portfolio import update_portfolio


def main():
    while True:
        try:
            bot_wait()  # waits a specified amount of seconds before starting the bot as a safety measure
            load_signals()  # loads signals into bot
            get_price()  # seed initial prices

            while True:
                orders, last_price, volume = buy()
                update_portfolio(orders, last_price, volume)
                coins_sold = sell_coins()
                remove_from_portfolio(coins_sold)

        except Exception:  # restarts bot if exception is caught (e.g. connection lost)
            print(f'{txcolors.WARNING}Error occured! Restarting bot in 1 min{txcolors.DEFAULT}')
            time.sleep(60)  # wait 1 min before restarting bot
            print("Trying to start again...")
            time.sleep(5)


def startup():
    try:
        debug_log("Start the bot", False)
        main()
    except KeyboardInterrupt:
        debug_log("Exit the bot", False)
        sell_all()


if __name__ == '__main__':
    debug_log("------------------------- START_BOT -------------------------", False)
    if login():  # verifies correct login data before starting the bot
        print_before_start()  # before commands can be used
        sys.stdout = StampedOut()  # timestamp

        while True:
            command = console_input()
            processing_input.input_check(command)
