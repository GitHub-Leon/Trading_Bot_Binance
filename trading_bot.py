# The main modules that executes the script repeatedly
import sys
import time

# local dependencies
from src.config import bot_wait
from src.console.input.console_input import console_input
from src.console.input.processing_input import input_check
from src.console.login import login
from src.console.output.exit import before_exit
from src.console.output.startup import startup
from src.helpers.scripts.sell_all_coins import sell_all
from src.remove_coins import remove_from_portfolio
from src.strategies.default.get_price import get_price
from src.strategies.default.sell import sell_coins
from src.strategies.default.trade import buy
from src.strategies.trading_view.signals import load_signals
from src.update_portfolio import update_portfolio
from src.classes.StampedOut import StampedOut
from src.classes.TxColor import txcolors


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


if __name__ == '__main__':
    if login():  # verifies correct login data before starting the bot
        startup()  # before commands can be used

        sys.stdout = StampedOut()  # timestamp

        while True:
            command = console_input()
            if command == "start":
                try:
                    main()
                except KeyboardInterrupt:
                    sell_all()
            elif command == "exit":
                before_exit()
                exit()
            else:
                input_check(command)
