# The main modules that executes the script repeatedly

# local dependencies
from src.login import login
from src.startup import startup
from src.exit import before_exit
from src.console_input import console_input
from src.console_input import input_check
from src.trade import buy
from src.sell import sell_coins
from src.update_portfolio import update_portfolio
from src.remove_coins import remove_from_portfolio
from src.config import bot_wait
from src.sell_all_coins import sell_all


def main():
    bot_wait()  # waits a specified amount of seconds before starting the bot as a safety measure

    while True:
        orders, last_price, volume = buy()
        update_portfolio(orders, last_price, volume)
        coins_sold = sell_coins()
        remove_from_portfolio(coins_sold)


if __name__ == '__main__':
    if login():  # verifies correct login data before starting the bot
        startup()  # before commands can be used
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
