import os
import json
import time

from binance.client import Client  # needed for the binance API and websockets

from .helpers import parameters
from .helpers import handle_creds

# global variables
global session_profit, historical_prices, hsp_head, volatility_cooloff, bot_paused
session_profit = 0
bot_paused = False


# Load arguments then parse settings
args = parameters.parse_args()

# Paths
WELCOME_TEXT_FILE = 'src/console/output/welcome.txt'
EMAIL_REGEX_FILE = './src/helpers/email_regex.txt'
PASSWORD_REGEX_FILE = './src/helpers/password_regex.txt'
BIRTHDAY_REGEX_FILE = './src/helpers/birthday_regex.txt'
VERIFICATION_MAIL_PLAIN_TEXT_FILE = './src/helpers/mail_verification_plain.txt'
VERIFICATION_MAIL_HTML_FILE = './src/helpers/mail_verification_html.html'

# YML
DEFAULT_CONFIG_FILE = 'config.yml'
DEFAULT_CREDS_FILE = 'creds.yml'
DEFAULT_CONFIG_AUTH_FILE = 'config_auth.yml'

config_file = args.config if args.config else DEFAULT_CONFIG_FILE
creds_file = args.creds if args.creds else DEFAULT_CREDS_FILE
auth_file = args.config if args.config else DEFAULT_CONFIG_AUTH_FILE
parsed_config = parameters.load_config(config_file)
parsed_creds = parameters.load_config(creds_file)
parsed_auth = parameters.load_config(auth_file)

DEBUG = True  # default False

# Load system vars
TEST_MODE = parsed_config['script_options']['TEST_MODE']
LOG_TRADES = parsed_config['script_options'].get('LOG_TRADES')
LOG_FILE = parsed_config['script_options'].get('LOG_FILE')
DEBUG_SETTING = parsed_config['script_options'].get('DEBUG')

# Load trading options
PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
TRADING_FEE = parsed_config['trading_options']['TRADING_FEE']
QUANTITY = parsed_config['trading_options']['QUANTITY']
CUSTOM_LIST = parsed_config['trading_options']['CUSTOM_LIST']
MAX_COINS = parsed_config['trading_options']['MAX_COINS']
FIATS = parsed_config['trading_options']['FIATS']
TIME_DIFFERENCE = parsed_config['trading_options']['TIME_DIFFERENCE']
RECHECK_INTERVAL = parsed_config['trading_options']['RECHECK_INTERVAL']

# Load strategy options
CHANGE_IN_PRICE = parsed_config['strategy_options']['volatility']['CHANGE_IN_PRICE']
USE_DEFAULT_STRATEGY = parsed_config['strategy_options']['volatility']['USE_DEFAULT_STRATEGY']
STOP_LOSS = parsed_config['strategy_options']['volatility']['STOP_LOSS']
TAKE_PROFIT = parsed_config['strategy_options']['volatility']['TAKE_PROFIT']
USE_TRAILING_STOP_LOSS = parsed_config['strategy_options']['trailing_sl']['USE_TRAILING_STOP_LOSS']
TRAILING_STOP_LOSS = parsed_config['strategy_options']['trailing_sl']['TRAILING_STOP_LOSS']
TRAILING_TAKE_PROFIT = parsed_config['strategy_options']['trailing_sl']['TRAILING_TAKE_PROFIT']
RSI_TIME_INTERVAL = parsed_config['strategy_options']['stoch_rsi']['TIME_INTERVAL']
RSI_PERIOD = parsed_config['strategy_options']['stoch_rsi']['PERIOD']
USE_STOCH_RSI = parsed_config['strategy_options']['stoch_rsi']['USE_STOCH_RSI']
RSI_BUY_TRIGGER = parsed_config['strategy_options']['stoch_rsi']['RSI_BUY_TRIGGER']
RSI_SELL_TRIGGER = parsed_config['strategy_options']['stoch_rsi']['RSI_SELL_TRIGGER']

# Load auth vars
SENDER_MAIL = parsed_auth['auth-options']['SENDER_MAIL']
SENDER_PW = parsed_auth['auth-options']['SENDER_MAIL_PW']
CODE_EXPIRE_DURATION = parsed_auth['auth-options']['CODE_EXPIRE_TIME']


if DEBUG_SETTING or args.debug:
    DEBUG = False

# Loads credentials
access_key, secret_key = handle_creds.load_correct_creds(parsed_creds, False)

if DEBUG:
    print(f'loaded config below\n{json.dumps(parsed_config, indent=4)}')
    print(f'Your credentials have been loaded from {creds_file}')

# Authenticate with the client
client = Client(access_key, secret_key)

# Use CUSTOM_LIST symbols if CUSTOM_LIST is set to True
if CUSTOM_LIST:
    tickers = [line.strip() for line in open('tickers.txt')]
else:
    tickers = None

# rolling window of prices; cyclical queue
historical_prices = [None] * (TIME_DIFFERENCE * RECHECK_INTERVAL)
hsp_head = -1

# try to load all the coins bought by the bot if the file exists and is not empty
coins_bought = {}

# path to the saved coins_bought file
coins_bought_file_path = 'coins_bought.json'

# prevent including a coin in volatile_coins if it has already appeared there less than TIME_DIFFERENCE minutes ago
volatility_cooloff = {}

# use separate files for testnet and live
if TEST_MODE:
    coins_bought_file_path = 'test_mode_' + coins_bought_file_path

# if saved coins_bought json file exists and it's not empty then load it
if os.path.isfile(coins_bought_file_path) and os.stat(coins_bought_file_path).st_size != 0:
    with open(coins_bought_file_path) as file:
        coins_bought = json.load(file)


def bot_wait():
    if not TEST_MODE:
        print('WARNING: You are using the Mainnet and live funds. Waiting 10 seconds as a security measure')
        time.sleep(10)

# signals = glob.glob("signals/*.exs")
#     for filename in signals:
#         for line in open(filename):
#             try:
#                 os.remove(filename)
#             except:
#                 if DEBUG: print(f'{txcolors.WARNING}Could not remove external signalling file {filename}{txcolors.DEFAULT}')
#
#     if os.path.isfile("signals/paused.exc"):
#         try:
#             os.remove("signals/paused.exc")
#         except:
#             if DEBUG: print(f'{txcolors.WARNING}Could not remove external signalling file {filename}{txcolors.DEFAULT}')
#
#     # load signalling modules
#     try:
#         if len(SIGNALLING_MODULES) > 0:
#             for module in SIGNALLING_MODULES:
#                 print(f'Starting {module}')
#                 mymodule[module] = importlib.import_module(module)
#                 t = threading.Thread(target=mymodule[module].do_work, args=())
#                 t.daemon = True
#                 t.start()
#                 time.sleep(2)
#         else:
#             print(f'No modules to load {SIGNALLING_MODULES}')
#     except Exception as e:
#         print(e)
