from binance.enums import *
import ast
from binance.client import Client
import config_tradingview


symbol = 'BTCBUSD'
client = Client(config_tradingview.API_KEY, config_tradingview.API_SECRET)


def send_order(symbol, side, quantity, order_type=ORDER_TYPE_MARKET):
    """Sends a order to binance"""
    order = {}
    try:
        print(f"sending order {order_type} - {side} {quantity} {symbol}")
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity
        )
    except Exception as e:
        pass

    return order


def parse_webhook(webhook_data):
    """Takes string and turns it into a py dict"""
    print(webhook_data)
    data = ast.literal_eval(webhook_data)
    return data
