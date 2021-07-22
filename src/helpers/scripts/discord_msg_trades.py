import requests

from src.config import MSG_DISCORD, DISCORD_WEBHOOK_TRADES
from src.helpers.scripts.logger import debug_log


def msg_discord(msg):
    debug_log("Push message to discord channel (trades)", False)

    try:
        message = msg + '\n\n'

        if MSG_DISCORD:
            mUrl = DISCORD_WEBHOOK_TRADES
            data = {"content": message}
            response = requests.post(mUrl, json=data)
    except Exception:
        debug_log("Error in discord messaging (trades)", True)
