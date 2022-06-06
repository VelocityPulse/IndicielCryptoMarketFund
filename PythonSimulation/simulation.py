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
        symbol_turn = 0
        fig = go.Figure()

        processed_crypto = []

        oldest_crypto = self.find_oldest_crypto(symbol_list)

        day_turn = 0
        for parent_day in oldest_crypto["days"]:
            for crypto in symbol_list:
                symbol_turn += 1
                if processed_crypto.__contains__(crypto):
                    continue
                x_list = []
                y_list = []
                if crypto["days"][0]["date"] == parent_day["date"]:
                    start_day = 0
                    for day in crypto["days"]:
                        if (day_turn + start_day) % multiple == 0:
                            x_list.append(day_turn + start_day)
                            # if day["top_position"] == -1:
                            #     y_list.append(0)
                            #     continue
                            y_list.append((day["top_position"] + 101 - day["top_position"] * 2))
                        start_day += 1
                    processed_crypto.append(crypto)
                    fig.add_trace(trace=go.Scatter(x=x_list, y=y_list, mode='lines+markers', name=crypto["name"]))

            day_turn += 1
            print("day n°" + str(day_turn))

            if symbol_turn == 30:
                fig.show()
                return
        fig.show()

        pass
