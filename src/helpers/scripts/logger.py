import csv
import os
import shutil
import threading
from datetime import datetime
from tempfile import NamedTemporaryFile

# Const vars
LOG_DIR = './log/'
PROFIT_LOG_DIR = LOG_DIR + 'profit_log.csv'
LOCK_DEBUG = threading.Lock()
LOCK_CONSOLE = threading.Lock()

if not os.path.exists('log'):  # only create folder, if it does not exist already
    os.mkdir('log')


def trade_log(logline):
    try:
        timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
        with LOCK_DEBUG:
            with open(f'{LOG_DIR}trades.log', 'a+') as f:
                f.write(f'{timestamp} {logline}\n')
    except:
        return False
    return True


def input_log(logline, is_valid):
    try:
        timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
        with LOCK_DEBUG:
            with open(f'{LOG_DIR}input.log', 'a+') as f:
                f.write(f'{timestamp} {"[V]" if is_valid else "[E]"} {logline}\n')
    except:
        return False
    return True


def debug_log(logline, is_error):
    try:
        timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
        with LOCK_DEBUG:
            with open(f'{LOG_DIR}debug_{datetime.today().strftime("%Y-%m-%d")}.log', 'a+') as f:
                f.write(f'{timestamp} {"[I]" if not is_error else "[E]"} {logline}\n')
    except Exception as e:
        console_log("Error while debug logging. Error-Message: " + str(e))
        return False
    return True


def console_log(logline):
    try:
        with LOCK_CONSOLE:
            print(logline)
    except Exception as e:
        debug_log("Error while console logging", True)
        return False
    return True


def profit_log(profit):
    debug_log("Log profits", False)
    """Logs the daily profit in a file"""
    found = False

    profit_list = []
    labels = ['Date', 'Profit']
    temp_file = NamedTemporaryFile(mode='w', delete=False)

    # creating the csv file with labels for each column
    try:
        if not os.path.exists(PROFIT_LOG_DIR):
            with open(PROFIT_LOG_DIR, 'a+', newline='') as file:
                # creating a csv writer object
                csvwriter = csv.writer(file)

                # set labels for all the coming rows
                csvwriter.writerow(labels)

        # check if there's an entry for the date already
        with open(PROFIT_LOG_DIR, 'r') as csv_file, temp_file:
            reader = csv.DictReader(csv_file, fieldnames=labels)
            writer = csv.DictWriter(temp_file, fieldnames=labels)

            for row in reader:
                if row['Date'] == str(datetime.today().strftime("%Y-%m-%d")):
                    found = True
                    row['Profit'] = str(profit + float(row['Profit']))
                row = {'Date': row['Date'], 'Profit': row['Profit']}
                writer.writerow(row)

        shutil.move(temp_file.name, PROFIT_LOG_DIR)
        if found: return

        # adds a new date entry to the file
        with open(PROFIT_LOG_DIR, 'a+', newline='') as file:
            # writing the fields
            row = [str(datetime.today().strftime("%Y-%m-%d")), str(profit)]

            # creating a csv writer object
            csvwriter = csv.writer(file)

            # add row to file
            csvwriter.writerow(row)

    except Exception as e:
        debug_log("Error in profit logging", True)
        console_log("Profit not logged due to Error")


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
