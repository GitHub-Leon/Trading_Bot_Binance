import os
from datetime import datetime

# Const vars
LOG_DIR = './log/'


if not os.path.exists('log'):  # only create folder, if it does not exist already
    os.mkdir('log')


def trade_log(logline):
    try:
            timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
            with open(f'{LOG_DIR}trades.log', 'a+') as f:
                f.write(f'{timestamp} {logline}\n')
    except:
        return False
    return True


def input_log(logline, is_valid):
    try:
        timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
        with open(f'{LOG_DIR}input.log', 'a+') as f:
            f.write(f'{timestamp} {"[V]" if is_valid else "[E]"} {logline}\n')
    except:
        return False
    return True


def debug_log(logline, is_error):
    try:
        timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
        with open(f'{LOG_DIR}debug_{datetime.today().strftime("%Y-%m-%d")}.log', 'a+') as f:
            f.write(f'{timestamp} {"[I]" if not is_error else "[E]"} {logline}\n')
    except Exception as e:
        debug_log("Error while debug logging. Error-Message: " + str(e), True)
        return False
    return True


def check_log_files():
    debug_log("Check how many log files exist", False)
    count_of_debug_files = 0
    oldest_file_date = datetime.today()
    log_files = os.listdir(LOG_DIR)
    for file in log_files:
        if file.split('_')[0] == f'debug':
            count_of_debug_files += 1
            if datetime.strptime(file.split('_')[1].split('.')[0], "%Y-%m-%d") < oldest_file_date:
                oldest_file_date = datetime.strptime(file.split('_')[1].split('.')[0], "%Y-%m-%d")

    debug_log(f'{count_of_debug_files} debug log files exist', False)
    if count_of_debug_files > 7:
        try:
            os.remove(f'{LOG_DIR}debug_{datetime.strftime(oldest_file_date, "%Y-%m-%d")}.log')
        except Exception as e:
            debug_log("Error while removing old log file. Error-Message: " + str(e), True)
        return True
    return False


debug_log("------------------------- START -------------------------", False)
if check_log_files():
    debug_log("Removed the oldest log file", False)
else:
    debug_log("No log file is removed", False)
