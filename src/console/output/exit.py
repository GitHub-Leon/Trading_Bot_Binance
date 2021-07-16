# local dependencies
from src.helpers.scripts.logger import debug_log, console_log


def init_exit():
    console_log("Thanks for using trading-bot.")

    debug_log("------------------------- EXIT -------------------------", False)
    exit()
