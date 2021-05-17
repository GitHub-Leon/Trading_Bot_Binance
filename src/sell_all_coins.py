from binance.helpers import round_step_size

# local dependencies
from src.colors import txcolors
from src.config import coins_bought, client, LOG_TRADES
from src.get_price import get_price
from src.save_trade import write_log
from src.remove_coins import remove_from_portfolio


def sell_all():
    current_prices = get_price()
    coins_sold = {}

    for coin in coins_bought:
        last_price = float(current_prices[coin]['price'])
        buy_price = float(coins_bought[coin]['bought_at'])
        price_change = float((last_price - buy_price) / buy_price * 100)

        # colored output depending on profit or loss
        if last_price < buy_price:
            print(f"{txcolors.SELL_LOSS}TP or SL reached, selling {coins_bought[coin]['volume']} {coin} - {buy_price} -> {last_price} : {price_change:.2f}%{txcolors.DEFAULT}")
        elif last_price > buy_price:
            print(f"{txcolors.SELL_PROFIT}TP or SL reached, selling {coins_bought[coin]['volume']} {coin} - {buy_price} -> {last_price} : {price_change:.2f}%{txcolors.DEFAULT}")

        try:
            try:
                rounded_amount = round_step_size(coins_bought[coin]['volume'], coins_bought[coin]['step_size'])
            except:
                tick_size = float(
                    next(
                        filter(
                            lambda f: f['filterType'] == 'LOT_SIZE',
                            client.get_symbol_info(coin)['filters']
                        )
                    )['stepSize']
                )
                rounded_amount = round_step_size(coins_bought[coin]['volume'], tick_size)

            client.create_order(
                symbol=coin,
                side='SELL',
                type='MARKET',
                quantity=rounded_amount,
            )

        except Exception as e:
            print(e)

        # run the else block if coin has been sold and create a dict for each coin sold
        else:
            coins_sold[coin] = coins_bought[coin]
            # Log trade

            if LOG_TRADES:
                profit = (last_price - buy_price) * coins_sold[coin]['volume']
                write_log(
                    f"Sell: {coins_sold[coin]['volume']} {coin} - {buy_price} - {last_price} Profit: {profit:.2f} {price_change:.2f}%")

    return coins_sold


remove_from_portfolio(sell_all())   # Executes sell_all and removes them from portfolio
