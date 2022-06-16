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

    def check_wallet_percent_is_equal_to_100(self, daily_wallet_collection):
        total_percent = 0
        for crypto in daily_wallet_collection.items():
            percent = crypto[1]["percent_importance"]
            if percent > 100 or percent < 0:
                percent
                assert False
            total_percent += percent

        assert total_percent == 100
        pass

    def start(self):
        symbol_list = self.getSymbols()

        multiple = 7
        starting_day = 3200
        # ending_day = 3312
        ending_day = 3230
        max_top_position = 10
        base_usdt_money = 50

        fig = go.Figure()
        oldest_crypto = self.find_oldest_crypto(symbol_list)
        self.calculateTotalMarketCap(symbol_list, oldest_crypto, max_top_position, starting_day, ending_day)
        day_turn = -1

        cloud_crypto_points = {}

        # Collecting all days in dictionary
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
                self.storeKeyToDict(cloud_crypto_points, day_turn, {day["name"]: day})
                # self.storeCloudPoints(cloud_crypto_points, crypto, day_turn, day)
            print("day n°" + str(day_turn))

        # Process backtesting
        daily_wallet_collection = {}
        day_turn = -1
        for item in cloud_crypto_points.items():  # Loop all days
            day_turn += 1
            x_list = []
            y_list = []

            # step 1 : buy all with base money
            # while the first day
            if day_turn == 0:
                for day_entry in item[1].items():  # Loop day of each crypto
                    day = day_entry[1]
                    if day["top_position"] >= max_top_position:
                        percent_importance = 0
                    else:
                        percent_importance = day["market_cap"] / day["total_market_cap"] * 100

                    theoretical_invest = base_usdt_money * percent_importance / 100
                    if not 0 <= theoretical_invest <= 100:
                        assert False

                    day.update({"percent_importance": percent_importance})
                    day.update({"usdt_invest": theoretical_invest})
                    day.update({"token_owned": theoretical_invest * day["price"]})  # add commission here
                    self.storeKeyToDict(daily_wallet_collection, day["name"], day)
                self.check_wallet_percent_is_equal_to_100(daily_wallet_collection)

            # step 2 : sell and buy with left money
            # while till the end
            if day_turn > 0:

                for day_entry in item[1].items():  # Loop day of each crypto
                    day = day_entry[1]
                    if day["top_position"] >= max_top_position:
                        percent_importance = 0
                    else:
                        percent_importance = day["market_cap"] / day["total_market_cap"] * 100

                    theoretical_invest = base_usdt_money * percent_importance / 100
                    if not 0 <= theoretical_invest <= 100:
                        assert False

                self.check_wallet_percent_is_equal_to_100(daily_wallet_collection)

                fig.add_trace(
                    trace=go.Scatter(x=x_list, y=y_list, mode='lines+markers', name=item[0]))

    def sell_losers(self, day, base_usdt_money):  # returns earn usdt money
        # sell x token too much compared to the percent_importance
        pass

    def buy_winners(self, day, base_usdt_money):  # returns
        pass

    def calculateTotalMarketCap(self, symbols, oldest_crypto, max_top_position, start_day, ending_day):
        turn = -1
        for parent_day in oldest_crypto["days"]:  # FOR ALL BITCOIN DAYS
            turn += 1

            if turn < start_day or turn > ending_day:
                continue

            presentAtThisDay = []
            print("Calculating total market cap for day n°" + str(turn))
            for crypto in symbols:
                if crypto["name"] == "okb":
                    crypto
                for day in crypto["days"]:
                    if day["date"] == parent_day["date"] and day["top_position"] < max_top_position:
                        presentAtThisDay.append(day)
                        break
            total_market_cap = 0
            for day in presentAtThisDay:
                total_market_cap += day["market_cap"]
            print("Total market cap : " + str(total_market_cap / 100000))
            for day in presentAtThisDay:
                day["total_market_cap"] = total_market_cap

    def storeKeyToDict(self, dict_, key, item):
        if key in dict_:
            dict_[key].update(item)
        else:
            dict_.update({key: item})

    def getDayByDate(self, crypto, date):
        for day in crypto["days"]:
            if day["date"] == date:
                return day
        return None
