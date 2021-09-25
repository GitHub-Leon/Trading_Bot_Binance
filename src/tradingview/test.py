from flask import Flask, request
from binance.enums import *
import json
from binance.client import Client
import config_tradingview

symbol = 'BTCBUSD'
app = Flask(__name__)

client = Client(config_tradingview.API_KEY, config_tradingview.API_SECRET)


def order(symbol, side, quantity, order_type=ORDER_TYPE_MARKET):

    order = {}
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity
        )
    except Exception as e:
        pass

    return order


@app.route('/')
def test():
    return 'tradingview_webhook'


@app.route('/webhook', methods=['POST'])
def webhook():
    data = json.loads(request.data)
    print(data)

    if data['passphrase'] != config_tradingview.WEBHOOK_PASSPHRASE:
        return {
            "code": "error",
            "message": "invalid passphrase"
        }

    side = data['strategy']['order_action'].upper()
    quantity = data['strategy']['position_size']

    order_response = order(side=side, symbol=symbol, quantity=quantity)

    print(order_response)
    if order_response:
        return {
            "code": "success",
            "message": "order succeeded"
        }
    else:
        return {
            "code": "failed",
            "message": "order failed"
        }
