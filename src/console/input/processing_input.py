# local dependencies
from src.console.output.exit import init_exit
from src.console.output.help import helps
from src.helpers.scripts import logger
from src.helpers.scripts.logger import debug_log
from src.settings import settings
from trading_bot import startup


def input_check(command):
    debug_log("Check input", False)
    functions = {
        "help": helps,
        "settings": settings,
        "exit": init_exit,
        "start": startup
    }
    # Get the function from functions dictionary
    func = functions.get(command)
    # Logging of command
    debug_log("Log the command", False)
    logging(command, callable(func))
    # Check if func is callable
    debug_log("Check if command is callable", False)
    if callable(func):
        # Execute the function
        func()
    else:
        debug_log("Command is not callable", False)


def logging(command, is_valid):
    if not is_valid:
        print("Invalid command")
    logger.input_log(command, is_valid)
