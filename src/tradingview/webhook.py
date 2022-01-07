from flask import Flask, request, abort
from .actions import *

# Flask object creation
app = Flask(__name__)


# Root to easily see if it's working
@app.route('/')
def root():
    return 'online'


@app.route('/webhook', methods=['POST'])
def webhook():
    data = parse_webhook(request.get_data(as_text=True))

    side = data['strategy']['order_action'].upper()
    symbol = data['ticker']
    quantity = data['strategy']['position_size']

    order_response = send_order(symbol=symbol, side=side, quantity=quantity)

    if order_response:
        return {
            "code": "success",
            "message": "order executed"
        }
    else:
        return {
            "code": "unsuccessful",
            "message": "order failed"
        }


if __name__ == '__main__':
    app.run()
