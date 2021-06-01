# local dependencies
from src.helpers.scripts.logger import debug_log


def console_input():
    debug_log("Enter input", False)
    return input("--> ")
