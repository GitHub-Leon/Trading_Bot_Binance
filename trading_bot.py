# The main modules that executes the script repeatedly

# local dependencies
from src.login import login
from src.config import bot_wait
from src.sell_all_coins import sell_all
from src.strategy_factory import strategy_factory


def main():
    bot_wait()  # waits a specified amount of seconds before starting the bot as a safety measure

    while True:
        strategy_factory()


if __name__ == '__main__':
    try:
        if login():  # verifies correct login data before starting the bot
            main()
    except KeyboardInterrupt:
        sell_all()
