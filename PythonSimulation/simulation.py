import json
import os

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

    def start(self):
        symbol_list = self.getSymbols()

        multiple = 30
        symbolTurn = 0
        x_list = []
        y_list = []
        fig = go.Figure()
        for symbol in symbol_list:
            symbolTurn += 1
            dayTurn = 0
            for day in symbol["days"]:
                if dayTurn % multiple == 0:
                    x_list.append(dayTurn)
                    y_list.append(day["top_position"])
                dayTurn += 1

            fig.add_trace(trace=go.Scatter(x=x_list, y=y_list, mode='lines+markers'))
            x_list = []
            y_list = []

            if symbolTurn == 4:
                fig.show()
                return

        pass
