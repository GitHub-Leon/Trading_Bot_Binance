# The main modules that executes the script repeatedly

# local dependencies
from src.login import login
from src.trade import buy
from src.sell import sell_coins
from src.update_portfolio import update_portfolio
from src.remove_coins import remove_from_portfolio


def main():
    while True:
        orders, last_price, volume = buy()
        update_portfolio(orders, last_price, volume)
        coins_sold = sell_coins()
        remove_from_portfolio(coins_sold)


if __name__ == '__main__':
    if login():
        main()
