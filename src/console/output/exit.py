# local dependencies
from src.helpers.scripts.logger import debug_log


def init_exit():
    print("Thanks for using trading-bot.")

    debug_log("------------------------- EXIT -------------------------", False)
    exit()
