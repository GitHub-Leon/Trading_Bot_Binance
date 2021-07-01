import threading
import time

from tradingview_ta import TA_Handler, Interval

# local dependencies
from src.config import SIGNALS_FOLDER, USE_LEVERAGE, coins_bought
from src.helpers.scripts.logger import debug_log

INTERVAL = Interval.INTERVAL_5_MINUTES  # Timeframe for analysis

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
SYMBOL = 'BTCUSDT'

LEVERAGE_UP_COIN = 'BTCUPUSDT'
LEVERAGE_DOWN_COIN = 'BTCDOWNUSDT'

THRESHOLD_BUY_BTCDOWN = 10  # x of 15 MA's indicating sell
THRESHOLD_SELL_BTCDOWN = 7  # x of 15 MA's indicating sell

THRESHOLD_BUY_BTCUP = 10  # x of 15 MA's indicating buy
THRESHOLD_SELL_BTCUP = 7  # x of 15 MA's indicating buy

TIME_TO_WAIT = 1  # Minutes to wait between analysis


def analyze():
    analysis = {}
    handler = {}

    handler = TA_Handler(
        symbol=SYMBOL,
        exchange=EXCHANGE,
        screener=SCREENER,
        interval=INTERVAL,
        timeout=10)

    try:
        analysis = handler.get_analysis()
    except Exception as e:
        debug_log("Error while custom_BTC_leverage. Error-Message:" + str(e), True)

    ma_sell = analysis.moving_averages['SELL']
    ma_buy = analysis.moving_averages['BUY']

    # buy
    if ma_sell >= THRESHOLD_BUY_BTCDOWN and LEVERAGE_DOWN_COIN not in list(coins_bought):
        debug_log(
            f'BTC_leverage: Sell signals at {ma_sell}/{THRESHOLD_BUY_BTCDOWN} -> Buying {LEVERAGE_DOWN_COIN}',
            False)
        print(
            f'BTC_leverage: Sell signals at {ma_sell}/{THRESHOLD_BUY_BTCDOWN} -> Buying {LEVERAGE_DOWN_COIN}')

        # write file down to buy LEVERAGE_DOWN_COIN
        with open(SIGNALS_FOLDER + '/buy_custom_BTC_leverage.exs', 'a+') as f:
            f.write(LEVERAGE_DOWN_COIN + '\n')
    if ma_buy >= THRESHOLD_BUY_BTCUP and LEVERAGE_UP_COIN not in list(coins_bought):
        debug_log(
            f'BTC_leverage: Buy signals at {ma_buy}/{THRESHOLD_BUY_BTCUP} -> Buying {LEVERAGE_UP_COIN}',
            False)
        print(
            f'BTC_leverage: Buy signals at {ma_buy}/{THRESHOLD_BUY_BTCUP} -> Buying {LEVERAGE_UP_COIN}')

        # write file down to buy LEVERAGE_UP_COIN
        with open(SIGNALS_FOLDER + '/buy_custom_BTC_leverage.exs', 'a+') as f:
            f.write(LEVERAGE_UP_COIN + '\n')

    # sell
    if ma_sell <= THRESHOLD_SELL_BTCDOWN and LEVERAGE_DOWN_COIN in list(coins_bought):
        debug_log(
            f'BTC_leverage: Sell signals at {ma_sell}/{THRESHOLD_BUY_BTCDOWN} -> Selling {LEVERAGE_DOWN_COIN}',
            False)
        print(
            f'BTC_leverage: Sell signals at {ma_sell}/{THRESHOLD_BUY_BTCDOWN} -> Selling {LEVERAGE_DOWN_COIN}')

        # write file down to sell LEVERAGE_DOWN_COIN
        with open(SIGNALS_FOLDER + '/sell_custom_BTC_leverage.exs', 'a+') as f:
            f.write(LEVERAGE_DOWN_COIN + '\n')
    if ma_buy <= THRESHOLD_SELL_BTCUP and LEVERAGE_UP_COIN in list(coins_bought):
        debug_log(
            f'BTC_leverage: Buy signals at {ma_buy}/{THRESHOLD_BUY_BTCUP} -> Selling {LEVERAGE_UP_COIN}',
            False)
        print(
            f'BTC_leverage: Buy signals at {ma_buy}/{THRESHOLD_BUY_BTCUP} -> Selling {LEVERAGE_UP_COIN}')

        # write file down to sell LEVERAGE_UP_COIN
        with open(SIGNALS_FOLDER + '/sell_custom_BTC_leverage.exs', 'a+') as f:
            f.write(LEVERAGE_UP_COIN + '\n')



def do_work():
    while True:
        if not threading.main_thread().is_alive() or not USE_LEVERAGE:
            exit()

        try:
            analyze()
        except Exception as e:
            debug_log("Error while using custom_BTC_leverage. Error-Message:" + str(e), True)

        time.sleep((TIME_TO_WAIT * 60))
