import sys
from src.helpers.scripts.logger import debug_log, console_log
from src.config import DEBUG, client, QUANTITY, TRADING_FEE

BNB_BUY_VALUE = QUANTITY * TRADING_FEE / 100
BNB_THRESHOLD = BNB_BUY_VALUE * 2  # x2 to ensure available balance


def is_enough_bnb_available():
    bnb_balance = float(client.get_asset_balance('BNB')['free'])
    bnb_price = float(client.get_symbol_ticker('BNBUSDT')['price'])

    bnb_value = bnb_balance * bnb_price  # calculate current bnb value

    return bnb_value > BNB_THRESHOLD  # return true if enough bnb is available


def buy_bnb():
    bnb_price = float(client.get_symbol_ticker('BNBUSDT')['price'])
    bnb_buy_amount = 0

    if BNB_BUY_VALUE < 15:  # buy if bnb_buy_value is below min_Notation
        bnb_buy_amount = float(15 / bnb_price)
    else:
        bnb_buy_amount = float(BNB_BUY_VALUE / bnb_price)

    buy_market = client.create_order(
        symbol='BNBUSDT',
        side='BUY',
        type='MARKET',
        quantity=bnb_buy_amount
    )

    debug_log(f"Successfully bought {bnb_buy_amount} BNB.", False)
    if DEBUG:
        console_log(f"Successfully bought {bnb_buy_amount} BNB.")


def do_work():
    try:
        if not is_enough_bnb_available():
            debug_log(f"Not enough BNB available.", True)
            if DEBUG:
                console_log(f'Not enough BNB available.')

            buy_bnb()

    except Exception as e:
        debug_log(f"Error in Module: {sys.argv[0]}. Couldn't buy BNB.", True)
        if DEBUG:
            console_log(f"Error in Module: {sys.argv[0]}\n. Couldn't buy BNB.")
