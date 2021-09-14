import matplotlib.pyplot as plt
import numpy as np

from src.config import MAX_COINS, QUANTITY, TEST_MODE
from src.helpers.scripts.binance_wallet_balance import total_amount_usdt
from src.helpers.scripts.logger import debug_log, console_log


# set start values, depending on paper or live-mode
start_value = QUANTITY * MAX_COINS
if not TEST_MODE:
    start_value = total_amount_usdt()


def plot_profit():
    debug_log("Trying to plot profits", False)
    try:
        profits = []
        profits_acc = []
        amount_trades = []

        # set the first value as the start_value
        profits_acc.append(start_value)

        # open the trades log file and read all lines
        with open('log/trades.log', 'r') as f:
            lines = f.readlines()
            if len(lines) < MAX_COINS+1:
                console_log("Not enough trades done yet.")
                return

        for line in lines:
            profit = line.split()[len(line.split()) - 1]  # get the last group of numbers/signs of every line

            if profit.find('%') != -1:  # check if line contains %
                profits.append(profit.split('%')[0])  # split for the number in front of the % sign

        for i in range(len(profits)):  # iterate through the profit strings
            profits_acc.append((1 + float(profits[i]) / 100) * QUANTITY - QUANTITY + profits_acc[
                i])  # append the newly calculated portfolio value to a list

        amount_trades.extend(range(0, len(profits)+1))

        # set interval for y-axis
        plt.xticks(np.arange(min(amount_trades), max(amount_trades), 1.0))

        # plotting the line 1 points
        plt.plot(amount_trades, profits_acc, label="Portfolio value")

        # naming the x axis
        plt.xlabel('Trade')
        # naming the y axis
        plt.ylabel('Value')
        # giving a title to my graph
        plt.title('Portfolio Graph')

        # show a legend on the plot
        plt.legend()

        # function to show the plot
        plt.show()
    except FileNotFoundError:
        console_log("File could not be found! No trades have been done yet!")
    except Exception as e:
        debug_log("Error in plot_profit.py " + str(e), True)
