import json

from src.classes.TxColor import txcolors
from src.config import creds_file, parsed_config, DEBUG, PRINT_CONFIG_AT_START
from src.helpers.scripts.logger import debug_log, console_log


def print_before_start():
    console_log('\n')  # print at every start

    if PRINT_CONFIG_AT_START or DEBUG:
        debug_log(f'Your credentials have been loaded from {creds_file}', False)
        console_log('\n' * 2)
        console_log(
            f'\t{txcolors.SELL_LOSS}{txcolors.BOLD}CURRENT CONFIG{txcolors.DEFAULT} \n\n '  # prints heading
            f'{json.dumps(parsed_config, indent=4)}')  # prints configs
        console_log('\n' * 4)
    if DEBUG:
        console_log(f'Your credentials have been loaded from {creds_file}')

    console_log(f'Tycoon Bot fully operational!')
    return True
