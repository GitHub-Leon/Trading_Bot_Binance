from src.strategy_options import strategy_options
from src.trading_options import trading_options


def console_input():
    return input("--> ")


def input_check(command):
    functions = {
        "trading_options": trading_options,
        "strategy_options": strategy_options
    }
    # Get the function from functions dictionary
    func = functions.get(command, lambda: print("Invalid command"))
    # Execute the function
    func()
