# The main modules that executes the script repeatedly
import time

from src.classes.TxColor import txcolors
from src.config import bot_wait
from src.console.input import processing_input
from src.console.input.console_input import console_input
from src.console.output.before_start import print_before_start
from src.helpers.scripts.logger import debug_log, console_log
from src.remove_coins import remove_from_portfolio
from src.strategies.default.get_price import get_price
from src.strategies.default.sell import sell_coins
from src.strategies.default.trade import buy
from src.strategies.trading_view.signals import load_signals
from src.update_globals import set_default_values
from src.update_portfolio import update_portfolio


def main():
    bot_wait()  # waits a specified amount of seconds before starting the bot as a safety measure

    try:  # separate exception catch, to prevent bot from loading modules after every error
        load_signals()  # loads signals into bot
    except Exception:
        console_log(f'{txcolors.WARNING}Error occured! Could not load signals{txcolors.DEFAULT}')
        exit()

    while True:
        try:
            get_price()  # seed initial prices

            while True:
                orders, last_price, volume = buy()
                update_portfolio(orders, last_price, volume)
                coins_sold = sell_coins()
                remove_from_portfolio(coins_sold)

        except Exception:  # restarts bot if exception is caught (e.g. connection lost)
            console_log(f'{txcolors.WARNING}Error occured! Restarting bot in 1 min{txcolors.DEFAULT}')
            time.sleep(60)  # wait 1 min before restarting bot
            console_log("Trying to start again...")
            time.sleep(5)


def startup():
    debug_log("------------------------- START_BOT -------------------------", False)
    try:
        debug_log("Start the bot", False)
        set_default_values()
        main()
    except KeyboardInterrupt:
        debug_log("Exit the bot", False)


if __name__ == '__main__':
    print_before_start()  # before commands can be used

    while True:
        command = console_input()
        processing_input.input_check(command)
