# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Alphavantage.co api key : T9742OP70MN4QXIG


# Press the green button in the gutter to run the script.
import sys

from backTestSimulation import BackTestSimulation
from fetchData import FetchData
from topSimulation import TopSimulation

if __name__ == '__main__':
    print("Start")

    if len(sys.argv) > 1 and sys.argv[1] == "fetch_data":
        f = FetchData()
        # f.fetch_data()
        # f.calculate_top_positions()

    elif len(sys.argv) > 1 and sys.argv[1] == "simulation":
        TopSimulation().start_v2()

    elif len(sys.argv) > 1 and sys.argv[1] == "backtest":
        BackTestSimulation().start()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
