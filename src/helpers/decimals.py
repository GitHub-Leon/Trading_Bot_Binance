# local dependencies
from src.config import PAIR_WITH


def is_fiat():
    # check if we are using a fiat as a base currency
    fiats = ['USDT', 'BUSD', 'AUD', 'BRL', 'EUR', 'GBP', 'RUB', 'TRY', 'TUSD', 'USDC', 'PAX', 'BIDR', 'DAI', 'IDRT', 'UAH', 'NGN', 'VAI', 'BVND']

    if PAIR_WITH in fiats:
        return True
    else:
        return False


def decimals():
    # set number of decimals for reporting fractions
    if is_fiat():
        return 2
    else:
        return 8
