import requests

from src.config import MSG_DISCORD, DISCORD_WEBHOOK
from src.helpers.scripts.logger import debug_log


def msg_discord(msg):
    debug_log("Push message to discord channel", False)

    try:
        message = msg + '\n\n'

        if MSG_DISCORD:
            mUrl = DISCORD_WEBHOOK
            data = {"content": message}
            response = requests.post(mUrl, json=data)
    except Exception:
        debug_log("Error in discord messaging", True)
