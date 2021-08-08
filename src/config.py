import json
import os
import time

from binance.client import Client  # needed for the binance API and websockets
from colorama import init

from src.helpers.scripts.logger import debug_log, console_log
from .helpers import handle_creds
from .helpers import parameters

# global variables
global session_profit, historical_prices, hsp_head, volatility_cooloff, bot_paused, sell_bearish

# Load arguments then parse settings
args = parameters.parse_args()
mymodule = {}

# YML
DEFAULT_CONFIG_FILE = 'config.yml'
DEFAULT_CREDS_FILE = 'creds.yml'

# Config loader
config_file = args.config if args.config else DEFAULT_CONFIG_FILE
creds_file = args.creds if args.creds else DEFAULT_CREDS_FILE
parsed_config = parameters.load_config(config_file, True)
parsed_creds = parameters.load_config(creds_file, True)

# Load system vars
TEST_MODE = parsed_config['script_options']['TEST_MODE']
MSG_DISCORD = parsed_config['script_options']['MSG_DISCORD']
LOG_TRADES = parsed_config['script_options'].get('LOG_TRADES')
AMERICAN_USER = parsed_config['script_options']['AMERICAN_USER']
DEBUG_SETTING = parsed_config['script_options']['DEBUG']
PRINT_CONFIG_AT_START = parsed_config['script_options']['PRINT_CONFIG_AT_START']

# Load trading options
PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
SELL_WHEN_BEARISH = parsed_config['trading_options']['SELL_WHEN_BEARISH']
SELL_ALL_AT_END = parsed_config['trading_options']['SELL_ALL_AT_END']
TRADING_FEE = parsed_config['trading_options']['TRADING_FEE']
QUANTITY = parsed_config['trading_options']['QUANTITY']
CUSTOM_LIST = parsed_config['trading_options']['CUSTOM_LIST']
USE_LEVERAGE = parsed_config['trading_options']['USE_LEVERAGE']
USE_LIMIT_ORDERS = parsed_config['trading_options']['USE_LIMIT_ORDERS']
MAX_COINS = parsed_config['trading_options']['MAX_COINS']
FIATS = parsed_config['trading_options']['FIATS']
TIME_DIFFERENCE = parsed_config['trading_options']['TIME_DIFFERENCE']
RECHECK_INTERVAL = parsed_config['trading_options']['RECHECK_INTERVAL']
STOP_LOSS = parsed_config['trading_options']['STOP_LOSS']
TAKE_PROFIT = parsed_config['trading_options']['TAKE_PROFIT']

# Load strategy options
CHANGE_IN_PRICE = parsed_config['strategy_options']['volatility']['CHANGE_IN_PRICE']
USE_DEFAULT_STRATEGY = parsed_config['strategy_options']['volatility']['USE_DEFAULT_STRATEGY']
USE_TRAILING_STOP_LOSS = parsed_config['strategy_options']['trailing_sl']['USE_TRAILING_STOP_LOSS']
TRAILING_STOP_LOSS = parsed_config['strategy_options']['trailing_sl']['TRAILING_STOP_LOSS']
TRAILING_TAKE_PROFIT = parsed_config['strategy_options']['trailing_sl']['TRAILING_TAKE_PROFIT']
SIGNALLING_MODULES = parsed_config['strategy_options']['trading_view']['SIGNALLING_MODULES']
USE_ELON_MIRROR = parsed_config['strategy_options']['elon_mirror']['USE_ELON_MIRROR']
USE_ONLY_ELON_MIRROR = parsed_config['strategy_options']['elon_mirror']['USE_ONLY_ELON_MIRROR']
ELON_MIRROR_RECHECK_INTERVAL = parsed_config['strategy_options']['elon_mirror']['RECHECK_INTERVAL']
BTC_BALANCE = parsed_config['strategy_options']['elon_mirror']['BTC_BALANCE']

# Elon recheck minimum 1 min
if ELON_MIRROR_RECHECK_INTERVAL < 1:
    ELON_MIRROR_RECHECK_INTERVAL = 1

# Paths
SIGNALS_FOLDER = 'src/signals'
TRADING_VIEW_FOLDER = 'src.strategies.trading_view'
if USE_LEVERAGE:
    CUSTOM_LIST_FILE = './tickers/tickers_leveraged.txt'
else:
    CUSTOM_LIST_FILE = './tickers/tickers_' + PAIR_WITH + '.txt'

# Desktop notification
DESKTOP_NOTIFICATIONS = True

# Packages
FREE_PACKAGE_ID = 999

DEBUG = False
if DEBUG_SETTING or args.debug:
    DEBUG = True

init()  # colorama

# Loads credentials
if MSG_DISCORD:
    DISCORD_WEBHOOK_TRADES = handle_creds.load_discord_trades_creds(parsed_creds)
    DISCORD_WEBHOOK_BALANCE = handle_creds.load_discord_balance_creds(parsed_creds)
else:
    DISCORD_WEBHOOK_TRADES = None
    DISCORD_WEBHOOK_BALANCE = None
access_key, secret_key = handle_creds.load_trading_creds(parsed_creds)

# Authenticate with the client
try:
    if AMERICAN_USER:
        client = Client(access_key, secret_key, tld='us')
    else:
        client = Client(access_key, secret_key)
except Exception:
    console_log("No connection to the internet.")
    exit()

# Use CUSTOM_LIST symbols if CUSTOM_LIST is set to True
if CUSTOM_LIST:
    tickers = [line.strip() for line in open(CUSTOM_LIST_FILE)]
else:
    tickers = None

# rolling window of prices; cyclical queue
historical_prices = [None] * (TIME_DIFFERENCE * RECHECK_INTERVAL)
hsp_head = -1
session_profit = 0
bot_paused = False
sell_bearish = False

# session results global vars
profitable_trades = 0
losing_trades = 0
session_fees = 0
session_duration = time.time()

# prevent including a coin in volatile_coins if it has already appeared there less than TIME_DIFFERENCE minutes ago
volatility_cooloff = {}

# try to load all the coins bought by the bot if the file exists and is not empty
coins_bought = {}

# path to the saved coins_bought file
coins_bought_file_path = 'coins_bought.json'

# use separate files for testnet and live
if TEST_MODE:
    coins_bought_file_path = 'test_mode_' + coins_bought_file_path

# if saved coins_bought json file exists and it's not empty then load it
if os.path.isfile(coins_bought_file_path) and os.stat(coins_bought_file_path).st_size != 0:
    with open(coins_bought_file_path) as file:
        coins_bought = json.load(file)


def bot_wait():
    if not TEST_MODE:
        debug_log("Mainnet security measure", False)
        console_log('WARNING: You are using the Mainnet and live funds. Waiting 1 second(s) as a security measure')
        time.sleep(1)
