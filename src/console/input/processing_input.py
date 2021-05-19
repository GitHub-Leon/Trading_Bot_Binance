from src.console.output.help import helps
from src.settings import settings


def input_check(command):
    functions = {
        "help": helps,
        "settings": settings
    }
    # Get the function from functions dictionary
    func = functions.get(command, lambda: print("Invalid command"))
    # Execute the function
    func()
