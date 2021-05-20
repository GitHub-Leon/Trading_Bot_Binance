import os
import json
import time

from binance.client import Client  # needed for the binance API and websockets

from .helpers import parameters
from .helpers import handle_creds

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

DEBUG = False

# Load system vars
TESTNET = parsed_config['script_options']['TESTNET']
LOG_TRADES = parsed_config['script_options'].get('LOG_TRADES')
LOG_FILE = parsed_config['script_options'].get('LOG_FILE')
DEBUG_SETTING = parsed_config['script_options'].get('DEBUG')

# Load trading vars
PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
QUANTITY = parsed_config['trading_options']['QUANTITY']
MAX_COINS = parsed_config['trading_options']['MAX_COINS']
FIATS = parsed_config['trading_options']['FIATS']
TIME_DIFFERENCE = parsed_config['trading_options']['TIME_DIFFERENCE']
RECHECK_INTERVAL = parsed_config['trading_options']['RECHECK_INTERVAL']
CHANGE_IN_PRICE = parsed_config['trading_options']['CHANGE_IN_PRICE']
STOP_LOSS = parsed_config['trading_options']['STOP_LOSS']
TAKE_PROFIT = parsed_config['trading_options']['TAKE_PROFIT']
CUSTOM_LIST = parsed_config['trading_options']['CUSTOM_LIST']
USE_TRAILING_STOP_LOSS = parsed_config['trading_options']['USE_TRAILING_STOP_LOSS']
TRAILING_STOP_LOSS = parsed_config['trading_options']['TRAILING_STOP_LOSS']
TRAILING_TAKE_PROFIT = parsed_config['trading_options']['TRAILING_TAKE_PROFIT']

# Load auth vars
SENDER_MAIL = parsed_auth['auth-options']['SENDER_MAIL']
SENDER_PW = parsed_auth['auth-options']['SENDER_MAIL_PW']
CODE_EXPIRE_DURATION = parsed_auth['auth-options']['CODE_EXPIRE_TIME']


# Database connection
DB_USERNAME = "bot"
DB_PASSWORD = "asdfasdf"
DB_NAME = "bot_2"


if DEBUG_SETTING or args.debug:
    DEBUG = False

# Loads credentials
# If Testnet true in config.yml, load test keys
access_key, secret_key = handle_creds.load_correct_creds(parsed_creds, TESTNET)

if DEBUG:
    print(f'loaded config below\n{json.dumps(parsed_config, indent=4)}')
    print(f'Your credentials have been loaded from {creds_file}')

# Authenticate with the client
client = Client(access_key, secret_key)

if TESTNET:
    # The API URL needs to be manually changed in the library to work on the TESTNET
    client.API_URL = 'https://testnet.binance.vision/api'

# Use CUSTOM_LIST symbols if CUSTOM_LIST is set to True
if CUSTOM_LIST:
    tickers = [line.strip() for line in open('tickers.txt')]
else:
    tickers = None

# try to load all the coins bought by the bot if the file exists and is not empty
coins_bought = {}

# path to the saved coins_bought file
coins_bought_file_path = 'coins_bought.json'

# use separate files for testnet and live
if TESTNET:
    coins_bought_file_path = 'testnet_' + coins_bought_file_path

# if saved coins_bought json file exists and it's not empty then load it
if os.path.isfile(coins_bought_file_path) and os.stat(coins_bought_file_path).st_size != 0:
    with open(coins_bought_file_path) as file:
        coins_bought = json.load(file)


def bot_wait():
    print('WARNING: You are using the Mainnet and live funds. Waiting 10 seconds as a security measure')
    time.sleep(10)
