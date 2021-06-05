import json

from src.config import creds_file, parsed_config, DEBUG, PRINT_CONFIG_AT_START
from src.helpers.scripts.logger import debug_log
from src.classes.TxColor import txcolors


def print_before_start():
    print('\n')  # print at every start

    if PRINT_CONFIG_AT_START or DEBUG:
        debug_log(f'Your credentials have been loaded from {creds_file}', False)
        print('\n' * 2)
        print(
            f'\t{txcolors.SELL_LOSS}{txcolors.BOLD}CURRENT CONFIG{txcolors.DEFAULT} \n\n '  # prints heading
            f'{json.dumps(parsed_config, indent=4)}')  # prints configs
        print('\n' * 4)
    if DEBUG:
        print(f'Your credentials have been loaded from {creds_file}')
    return True
