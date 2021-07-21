import time

from src.config import SELL_ALL_AT_END
from src.helpers.scripts.logger import debug_log, console_log
from src.helpers.scripts.sell_all_coins import sell_all


def init_exit():
    if SELL_ALL_AT_END:
        sell_all()
    console_log("Thanks for using trading-bot.")
    end_of_session_results()

    debug_log("------------------------- EXIT -------------------------", False)
    exit()


def end_of_session_results():
    # import updated globals
    from src.config import profitable_trades, losing_trades, coins_bought, session_duration, session_profit, QUANTITY, \
        PAIR_WITH, session_fees

    hours, rem = divmod(time.time() - session_duration, 3600)
    minutes, seconds = divmod(rem, 60)

    debug_log("Print session results", False)

    console_log("")
    console_log(f"Profitable trades: {profitable_trades}")
    console_log(f"Losing trades: {losing_trades}")
    console_log(f"Amount not sold: {len(coins_bought)}")
    console_log("Session duration: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
    console_log("Session profit: {:.2f} {}".format(session_profit, PAIR_WITH))
    console_log("Fees spent approximately: {:.2f} {}".format(session_fees, PAIR_WITH))
    console_log(
        f"Trading Volume approximately: {QUANTITY * (losing_trades + profitable_trades + len(coins_bought))} {PAIR_WITH}")
