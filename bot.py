from binance.client import Client  # needed for the binance API and websockets
from datetime import datetime, timedelta
from itertools import count
from dotenv import load_dotenv  # used to load environmental variables
from colorama import init

import time
import json
import os

# loads environmental variables
load_dotenv()

init()  # coloring console output

TESTNET = False

API_KEY_TESTNET = os.getenv('API_KEY_TESTNET')
API_SECRET_TESTNET = os.getenv('API_SECRET_TESTNET')

API_KEY_LIVE = os.getenv('API_KEY_LIVE')
API_SECRET_LIVE = os.getenv('API_SECRET_LIVE')

if TESTNET:
    client = Client(API_KEY_TESTNET, API_SECRET_TESTNET)

    # The API URL needs to be manually changed in the library to work on the TESTNET
    client.API_URL = 'https://testnet.binance.vision/api'

else:
    client = Client(API_KEY_LIVE, API_SECRET_LIVE)

# Strategies
USE_SIMPLE = True  # buys at % increase and sells if TP or SL is triggered
USE_TRAILING_STOP_LOSS = True  # keeps upping the SL from the last price until it's met

# PARAMS
CUSTOM_LIST = False  # Use custom tickers.txt list for filtering pairs
PAIR_WITH = 'USDT'
QUANTITY = 15  # Value in PAIR_WITH
MAX_COINS = 10  # Max numbers of coins to hold
FIATS = ['EURUSDT', 'GBPUSDT', 'JPYUSDT', 'USDUSDT', 'DOWN', 'UP']  # Pairs to exclude
TIME_DIFFERENCE = 2  # Difference in minutes before new calculation of current price
RECHECK_INTERVAL = 10  # Number of times to check for TP/SL during each TIME_DIFFERENCE (Minimum 1)
CHANGE_IN_PRICE = 2  # Change in price to trigger buy order in %
STOP_LOSS = 1.5  # Percentage loss for stop-loss trigger
TAKE_PROFIT = 0.3  # At what percentage increase of buy value profits will be taken

# when hit TAKE_PROFIT, move STOP_LOSS to TRAILING_STOP_LOSS percentage points below TAKE_PROFIT hence locking in profit
# when hit TAKE_PROFIT, move TAKE_PROFIT up by TRAILING_TAKE_PROFIT percentage points
TRAILING_STOP_LOSS = 2
TRAILING_TAKE_PROFIT = 2

# Use log file for trades
LOG_TRADES = True
LOG_FILE = 'trades.txt'

# Debug for additional console output
DEBUG = True

# END OF CONFIG

# try to load all the coins bought by the bot if the file exists and is not empty
coins_bought = {}
tickers = []  # ticker list for coin pairs

# path to the saved coins_bought file
coins_bought_file_path = 'coins_bought.json'

# use separate files for testnet and live
if TESTNET:
    coins_bought_file_path = 'testnet_' + coins_bought_file_path

# if saved coins_bought json file exists and it's not empty then load it
if os.path.isfile(coins_bought_file_path) and os.stat(coins_bought_file_path).st_size != 0:
    with open(coins_bought_file_path) as file:
        coins_bought = json.load(file)


# for colors in console output
class txcolors:
    BUY = '\033[92m'
    WARNING = '\033[93m'
    SELL = '\033[91m'
    DEFAULT = '\033[39m'


# Load custom tickerlist from file tickers.txt into array tickers
if CUSTOM_LIST:
    tickers = [line.strip() for line in open('tickers.txt')]


def get_price():
    """Return the current price for all coins on binance"""

    initial_price = {}
    prices = client.get_all_tickers()

    for coin in prices:

        # Only return USDT pairs and exclude margin symbols like BTCDOWNUSDT, filter by custom list if defined.

        if CUSTOM_LIST:
            if any(item + PAIR_WITH == coin['symbol'] for item in tickers) and all(
                    item not in coin['symbol'] for item in FIATS):
                initial_price[coin['symbol']] = {'price': coin['price'], 'time': datetime.now()}
        else:  # only Return coin(PAIR_WITH) pairs and exclude margin symbols like BTCDOWNUSDT
            if PAIR_WITH in coin['symbol'] and all(item not in coin['symbol'] for item in FIATS):
                initial_price[coin['symbol']] = {'price': coin['price'], 'time': datetime.now()}

    return initial_price


def wait_for_price():
    """calls the initial price and ensures the correct amount of time has passed
    before reading the current price again"""

    volatile_coins = {}
    initial_price = get_price()

    while initial_price['BNB' + PAIR_WITH]['time'] > datetime.now() - timedelta(seconds=TIME_DIFFERENCE):
        i = 0
        while i < RECHECK_INTERVAL:
            print(f'checking TP/SL...')
            coins_sold = sell_coins()
            remove_from_portfolio(coins_sold)
            time.sleep((TIME_DIFFERENCE / RECHECK_INTERVAL))
            i += 1
        time.sleep(60 * TIME_DIFFERENCE)

    else:
        last_price = get_price()

        # calculate the difference between the first and last price reads
        for coin in initial_price:
            threshold_check = (float(last_price[coin]['price']) - float(initial_price[coin]['price'])) / float(
                initial_price[coin]['price']) * 100

            # each coin with higher gains than our CHANGE_IN_PRICE is added to the volatile_coins dict
            # if less than MAX_COINS is not reached.
            if threshold_check > CHANGE_IN_PRICE:
                if len(coins_bought) < MAX_COINS:
                    volatile_coins[coin] = threshold_check
                    volatile_coins[coin] = round(volatile_coins[coin], 3)

        return volatile_coins, len(volatile_coins), last_price


def convert_volume():
    """Converts the volume given in QUANTITY from coin (PAIR_WITH) to the each coin's volume"""

    volatile_coins, number_of_coins, last_price = wait_for_price()
    lot_size = {}
    volume = {}

    for coin in volatile_coins:

        # Find the correct step size for each coin
        try:
            info = client.get_symbol_info(coin)
            step_size = info['filters'][2]['stepSize']
            lot_size[coin] = step_size.index('1') - 1

            if lot_size[coin] < 0:
                lot_size[coin] = 0

        except:
            pass

        # calculate the volume in coin from QUANTITY in coin (PAIR_WITH)
        volume[coin] = float(QUANTITY / float(last_price[coin]['price']))

        # define the volume with the correct step size
        if coin not in lot_size:
            volume[coin] = float('{:.1f}'.format(volume[coin]))

        else:
            # if lot size has 0 decimal points, make the volume an integer
            if lot_size[coin] == 0:
                volume[coin] = int(volume[coin])
            else:
                volume[coin] = float('{:.{}f}'.format(volume[coin], lot_size[coin]))

    return volume, last_price


def buy():
    """Place Buy market orders for each volatile coin found"""

    volume, last_price = convert_volume()
    orders = {}

    for coin in volume:

        # only buy if the there are no active trades on the coin
        if coin not in coins_bought:
            print(f"{txcolors.BUY}Preparing to buy {volume[coin]} {coin}{txcolors.DEFAULT}")

            if TESTNET:
                # create test order before pushing an actual order
                test_order = client.create_test_order(symbol=coin, side='BUY', type='MARKET', quantity=volume[coin])

            # try to create a real order if the test orders did not raise an exception
            try:
                buy_limit = client.create_order(
                    symbol=coin,
                    side='BUY',
                    type='MARKET',
                    quantity=volume[coin]
                )

            # error handling here in case position cannot be placed
            except Exception as e:
                print(e)

            # run the else block if the position has been placed and return order info
            else:
                orders[coin] = client.get_all_orders(symbol=coin, limit=1)

                # binance sometimes returns an empty list, the code will wait here until binance returns the order
                while not orders[coin]:
                    orders[coin] = client.get_all_orders(symbol=coin, limit=1)
                    time.sleep(1)

                else:
                    # Log trade
                    if LOG_TRADES:
                        write_log(f"Buy : {volume[coin]} {coin} - {last_price[coin]['price']}")

    return orders, last_price, volume


def sell_coins():
    """sell coins that have reached the STOP LOSS or TAKE PROFIT threshold"""

    last_price = get_price()
    coins_sold = {}

    for coin in list(coins_bought):
        # define stop loss and take profit
        TP = float(coins_bought[coin]['bought_at']) + (
                    float(coins_bought[coin]['bought_at']) * coins_bought[coin]['take_profit']) / 100
        SL = float(coins_bought[coin]['bought_at']) + (
                    float(coins_bought[coin]['bought_at']) * coins_bought[coin]['stop_loss']) / 100

        LastPrice = float(last_price[coin]['price'])
        BuyPrice = float(coins_bought[coin]['bought_at'])
        PriceChange = float((LastPrice - BuyPrice) / BuyPrice * 100)


        # check that the price is above the take profit and readjust SL and TP accordingly if trialing stop loss used
        if float(last_price[coin]['price']) > TP and USE_TRAILING_STOP_LOSS:
            print("TP reached, adjusting TP and SL accordingly to lock-in profit")

            # increasing TP by TRAILING_TAKE_PROFIT (essentially next time to readjust SL)
            coins_bought[coin]['take_profit'] += TRAILING_TAKE_PROFIT
            coins_bought[coin]['stop_loss'] = coins_bought[coin]['take_profit'] - TRAILING_STOP_LOSS
            print(f"TP or SL reached, selling {coins_bought[coin]['volume']} {coin}...")


        # check that the price is below the stop loss or above take profit (if trailing stop loss not used) and sell if this is the case
        if float(last_price[coin]['price']) < SL or (float(last_price[coin]['price']) > TP and not USE_TRAILING_STOP_LOSS):
            if TESTNET:
                # create test order before pushing an actual order
                test_order = client.create_test_order(symbol=coin, side='SELL', type='MARKET',
                                                      quantity=coins_bought[coin]['volume'])

            # try to create a real order if the test orders did not raise an exception
            try:
                # sell 99.25% of the coin (0.75% for trading fees)
                sell_amount = coins_bought[coin]['volume'] * 99.25 / 100
                decimals = len(str(coins_bought[coin]['volume']).split("."))

                # color profit/loss output per trade
                profit_loss = round(
                    (float(last_price[coin]['price']) / float(coins_bought[coin]['bought_at']) * 100 - 100.15), 2)
                if profit_loss > 0:
                    print("Sold for: " + '\033[92m' + str(profit_loss) + "%" + '\033[0m')
                else:
                    print("Sold for: " + '\033[93m' + str(profit_loss) + "%" + '\033[0m')

                # convert to correct volume
                sell_amount = float('{:.{}f}'.format(sell_amount, decimals))

                sell_coins_limit = client.create_order(
                    symbol=coin,
                    side='SELL',
                    type='MARKET',
                    quantity=coins_bought[coin]['volume']
                )

            # in case position cannot be placed
            except Exception as e:
                print(e)

            # run the else block if coin has been sold and create a dict for each coin sold
            else:
                coins_sold[coin] = coins_bought[coin]
                if LOG_TRADES:
                    profit = (LastPrice - BuyPrice) * coins_sold[coin]['volume']
                    write_log(
                        f"Sell: {coins_sold[coin]['volume']} {coin} - {BuyPrice} - {LastPrice} Profit: {profit:.2f} {PriceChange:.2f}%")

            print(f'TP or SL not yet reached, not selling {coin} for now {BuyPrice} - {LastPrice} : {PriceChange:.2f}% ')

    return coins_sold


def update_portfolio(orders, last_price, volume):
    """add every coin bought to our portfolio for tracking/selling later"""

    if DEBUG: print(orders)

    for coin in orders:
        coins_bought[coin] = {
            'symbol': orders[coin][0]['symbol'],
            'orderid': orders[coin][0]['orderId'],
            'timestamp': orders[coin][0]['time'],
            'bought_at': last_price[coin]['price'],
            'volume': volume[coin],
            'stop_loss': -STOP_LOSS,
            'take_profit': TAKE_PROFIT,
        }

        # save coins in a json file in the same directory
        with open(coins_bought_file_path, 'w') as file:
            json.dump(coins_bought, file, indent=4)

        print(f'Order with id {orders[coin][0]["orderId"]} placed and saved to file')


def remove_from_portfolio(coins_sold):
    """Remove coins sold due to SL or TP from portfolio"""
    for coin in coins_sold:
        coins_bought.pop(coin)

    with open(coins_bought_file_path, 'w') as file:
        json.dump(coins_bought, file, indent=4)


def write_log(log_line):
    timestamp = datetime.now().strftime("%d.%m %H:%M:%S")
    with open(LOG_FILE, 'a+') as f:
        f.write(timestamp + ' ' + log_line + '\n')


if __name__ == '__main__':
    print('Press Ctrl-Q to stop the script')

    if not TESTNET:
        print(
            'WARNING: You are using the Mainnet and live funds. Waiting 30 seconds as a security measure')
        time.sleep(30)

    for i in count():
        orders, last_price, volume = buy()
        update_portfolio(orders, last_price, volume)
        coins_sold = sell_coins()
        remove_from_portfolio(coins_sold)
