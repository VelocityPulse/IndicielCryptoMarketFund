import json
import os
import sys

import plotly.graph_objects as go


class Simulation:
    data_path = "../IndicielCryptoMarket/data/"
    symbols_path = "processedSymbols/"

    def __init__(self):
        pass

    def getSymbols(self):
        json_list = []

        for file in os.listdir(self.data_path + self.symbols_path):
            with open(self.data_path + self.symbols_path + file, "r") as f:
                json_list.append(json.loads(f.read()))
        return json_list

    @staticmethod
    def find_oldest_crypto(json_list):
        ret = 0
        time_ref = sys.maxsize

        for crypto in json_list:
            if crypto["days"][0]["date"] < time_ref:
                time_ref = crypto["days"][0]["date"]
                ret = crypto
        return ret

    def start(self):
        symbol_list = self.getSymbols()

        multiple = 1
        stopping_end = 20
        starting_day = 3000

        fig = go.Figure()
        processed_crypto = []
        oldest_crypto = self.find_oldest_crypto(symbol_list)
        day_turn = 0
        symbol_turn = 0
        for parent_day in oldest_crypto["days"]:

            for crypto in symbol_list:
                symbol_turn += 1
                if processed_crypto.__contains__(crypto):
                    continue
                x_list = []
                y_list = []
                if crypto["days"][0]["date"] == parent_day["date"]:
                    first_crypto_day = 0
                    for day in crypto["days"]:
                        if day["top_position"] == -1:
                            continue

                        if day_turn + first_crypto_day > len(oldest_crypto["days"]) - stopping_end:
                            continue

                        top_position = day["top_position"] + 101 - day["top_position"] * 2
                        if (day_turn + first_crypto_day) % multiple == 0 and top_position > 50:

                            if day_turn + first_crypto_day > starting_day:
                                x_list.append(day_turn + first_crypto_day)
                                y_list.append(top_position)
                        first_crypto_day += 1

                    processed_crypto.append(crypto)
                    fig.add_trace(trace=go.Scatter(x=x_list, y=y_list, mode='lines+markers', name=crypto["name"]))

            day_turn += 1
            print("day n°" + str(day_turn))

        fig.show()

        pass
