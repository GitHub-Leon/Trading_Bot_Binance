# local dependencies
from src.config import client
from src.strategies.default.get_price import get_price

# Getting account info to check balance
info = client.get_account()  # Getting account info

token_pairs = []  # List to hold different token pairs


def get_balances():
    # Saving different tokens and respective quantities into lists
    assets = []
    values = []
    for index in range(len(info['balances'])):
        for key in info['balances'][index]:
            if key == 'asset':
                assets.append(info['balances'][index][key])
            if key == 'free':
                values.append(float(info['balances'][index][key]) + float(info['balances'][index]['locked']))

    # Creating token pairs and saving into a list
    for token in assets:
        if token != 'USDT':
            token_pairs.append(token + 'USDT')

    return assets, values


def get_current_prices():
    prices = get_price(False, True)
    return prices


def total_amount_usdt():
    """
        Function to calculate total portfolio value in USDT
        :return: total value in USDT
        """
    assets, values = get_balances()
    token_usdt = get_current_prices()

    total_amount = 0
    for i, token in enumerate(assets):
        if token != 'USDT':
            try:
                total_amount += float(values[i]) * float(token_usdt[token + 'USDT']['price'])
            except Exception:  # if coin isn't available for trading or not listed anymore, ignore it
                pass
        else:
            total_amount += float(values[i]) * 1
    return total_amount


def total_amount_btc():
    """
        Function to calculate total portfolio value in BTC
        :return: total value in BTC
        """
    assets, values = get_balances()
    token_usdt = get_current_prices()

    total_amount = 0
    for i, token in enumerate(assets):
        if token != 'BTC' and token != 'USDT':
            try:
                total_amount += float(values[i]) * float(token_usdt[token + 'USDT']['price']) / float(token_usdt['BTCUSDT']['price'])
            except Exception:  # if coin isn't available for trading or not listed anymore, ignore it
                pass
        if token == 'BTC':
            total_amount += float(values[i]) * 1
        else:
            total_amount += float(values[i]) / float(token_usdt['BTCUSDT']['price'])

    return total_amount


def assets_usdt():
    """
        Function to convert all assets into equivalent USDT value
        :return: list of asset values in USDT
        """
    assets, values = get_balances()
    token_usdt = get_current_prices()

    assets_in_usdt = []
    for i, token in enumerate(assets):
        if token != 'USDT':
            try:
                print(float(values[i]) * float(token_usdt[token + 'USDT']['price']))
                assets_in_usdt.append(float(values[i]) * float(token_usdt[token + 'USDT']['price']))
            except Exception:  # if coin isn't available for trading or not listed anymore, ignore it
                pass
        else:
            assets_in_usdt.append(float(values[i]) * 1)

    return assets_in_usdt
