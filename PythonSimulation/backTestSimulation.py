import json
import os
import sys

import plotly.graph_objects as go


class BackTestSimulation:
    data_path = "../IndicielCryptoMarket/data/"
    symbols_path = "processedSymbols/"

    def getSymbols(self):
        json_list = []

        for file in os.listdir(self.data_path + self.symbols_path):
            with open(self.data_path + self.symbols_path + file, "r") as f:
                json_list.append(json.loads(f.read()))
        return json_list

    def find_oldest_crypto(self, json_list):
        ret = 0
        time_ref = sys.maxsize

        for crypto in json_list:
            if crypto["days"][0]["date"] < time_ref:
                time_ref = crypto["days"][0]["date"]
                ret = crypto
        return ret

    def start(self):
        symbol_list = self.getSymbols()

        multiple = 7
        starting_day = 3200
        ending_day = 3312
        max_top_position = 50

        fig = go.Figure()
        oldest_crypto = self.find_oldest_crypto(symbol_list)
        self.calculateTotalMarketCap(symbol_list, oldest_crypto, max_top_position, starting_day, ending_day)
        day_turn = -1

        cloud_crypto_points = {}

        for parent_day in oldest_crypto["days"]:  # FOR ALL BITCOIN DAYS
            day_turn += 1

            if day_turn > ending_day:
                break
            if day_turn < starting_day:
                continue

            if day_turn % multiple != 0:
                continue

            for crypto in symbol_list:
                day = self.getDayByDate(crypto, parent_day["date"])
                if day is None:
                    continue

                if day["top_position"] > max_top_position:
                    continue

                self.storeCloudPoints(cloud_crypto_points, crypto, day_turn, day)

            print("day n°" + str(day_turn))

        for item in cloud_crypto_points.items():
            x_list = []
            y_list = []
            price_list = []
            for entry in item[1].items():
                x_list.append(entry[0])
                day = entry[1]
                top_position = day["top_position"] + 101 - (day["top_position"] * 2)
                y_list.append(top_position)
                # TODO
                price_list.append(day["price"])

            fig.add_trace(
                trace=go.Scatter(x=x_list, y=y_list, mode='lines+markers', name=item[0], hovertext=price_list))

        fig.show()
        pass

    def calculateTotalMarketCap(self, symbols, oldest_crypto, max_top_position, start_day, ending_day):
        presentAtThisDay = []
        turn = -1
        for parent_day in oldest_crypto["days"]:  # FOR ALL BITCOIN DAYS
            turn += 1
            if turn < start_day or turn > ending_day:
                continue
            print("Calculating total market cap for day n°" + str(turn))
            for crypto in symbols:
                for day in crypto["days"]:
                    if day["date"] == parent_day["date"] and day["top_position"] < max_top_position:
                        presentAtThisDay.append(day)
                        break
            total_market_cap = 0
            for day in presentAtThisDay:
                total_market_cap += day["market_cap"]
            for day in presentAtThisDay:
                day["total_market_cap"] = total_market_cap

    def storeCloudPoints(self, cloud_crypto_points, crypto, day_turn, day):
        new_point = {day_turn: day}
        if crypto["name"] in cloud_crypto_points:
            cloud_crypto_points[crypto["name"]].update(new_point)
        else:
            new_crypto = {crypto["name"]: {}}
            cloud_crypto_points.update(new_crypto)
            cloud_crypto_points[crypto["name"]].update(new_point)

    def getDayByDate(self, crypto, date):
        for day in crypto["days"]:
            if day["date"] == date:
                return day
        return None
