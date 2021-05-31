# This module converts the use-given volume from PAIR_WITH to the coin that gets bought

from src.config import QUANTITY, client, DEBUG
# local dependencies
from src.strategies.default.wait_for_price import wait_for_price


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

        except Exception as e:
            if DEBUG:
                print(e)

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
