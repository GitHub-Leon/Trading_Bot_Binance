# needed for the binance API and websockets
from binance.client import Client
import csv
import os
import time
from datetime import date, datetime

client = Client()


def get_historical_data(coin, since, kline_interval):
    """
    Args example:
    coin = 'BTCUSDT'
    since = '1 Jan 2021'
    kline_interval = Client.KLINE_INTERVAL_1MINUTE
    """
    if not os.path.exists('src/backtesting_data'):  # creates directory for backtest data
        os.makedirs('src/backtesting_data')

    if os.path.isfile(f'src/backtesting_data/{coin}_{since}_{kline_interval}.csv'):  # creates file for coin data
        print('Datafile already exists, loading file...')

    else:
        print(f'Fetching historical data, this may take a few minutes...')

        start_time = time.perf_counter()
        data = client.get_historical_klines(coin, kline_interval, since)
        data = [item[0:5] for item in data]

        # field names
        fields = ['timestamp', 'high', 'low', 'open', 'close']

        # save the data
        with open(f'src/backtesting_data/{coin}_{since}_{kline_interval}.csv', 'w', newline='') as f:

            # using csv.writer method from CSV package
            write = csv.writer(f)

            write.writerow(fields)
            write.writerows(data)

        end_time = time.perf_counter()

        # calculate how long it took to produce the file
        time_elapsed = round(end_time - start_time)

        print(f'Historical data for {coin} saved as {coin}_{since}_{kline_interval}.csv. Time elapsed: {time_elapsed} seconds')
    return f'src/backtesting_data/{coin}_{since}_{kline_interval}.csv'
