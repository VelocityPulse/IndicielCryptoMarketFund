# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Alphavantage.co api key : T9742OP70MN4QXIG


# Press the green button in the gutter to run the script.
import sys

from fetchData import FetchData
from simulation import Simulation

if __name__ == '__main__':
    print("Start")

    if len(sys.argv) > 1 and sys.argv[1] == "fetch_data":
        FetchData().fetch_data()
    elif len(sys.argv) > 1 and sys.argv[1] == "simulation":
        Simulation().start()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
