# Module that logs all trades including PNL

from datetime import datetime

# local dependencies
from src.config import LOG_FILE


def write_log(logline):
    timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
    with open(LOG_FILE, 'a+') as f:
        f.write(timestamp + ' ' + logline + '\n')
