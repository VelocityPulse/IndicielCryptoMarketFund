import json
import os
import sys

import plotly.graph_objects as go


class BackTestSimulation:
    data_path = "../IndicielCryptoMarket/data/"
    symbols_path = "processedSymbols/"

    class Parameters:
        multiple = 7
        starting_day = 3100
        ending_day = 3230
        max_top_position = 10
        starting_usdt_money = 50


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

    def check_total_percent_importance_is_equal_to_100(self, daily_wallet_collection):
        total_percent = 0
        for crypto in daily_wallet_collection.items():
            percent = crypto[1]["percent_importance"]
            if percent > 100 or percent < 0:
                percent
                assert False
            total_percent += percent

        assert round(total_percent) == 100
        pass

    def start(self):
        symbol_list = self.getSymbols()

        parameters = self.Parameters()

        fig = go.Figure()
        oldest_crypto = self.find_oldest_crypto(symbol_list)
        self.calculateTotalMarketCap(symbol_list, oldest_crypto, parameters)

        # Cloud crypto points is a dictionary where each key is a day index that contains a list of
        # the day of each present crypto at this moment
        cloud_crypto_points = self.collectingAllDaysInDictionary(oldest_crypto, symbol_list, parameters)

        # Process backtesting
        last_day_list_of_crypto = {}
        day_turn = -1
        for day_list_of_crypto in cloud_crypto_points.values():  # Loop all days
            day_turn += 1
            # x_list = []
            # y_list = []
            daily_wallet_collection = {}

            # STEP 1 : buy all with base money
            # ONLY THE FIRST DAY
            if day_turn == 0:
                for day in day_list_of_crypto.values():  # Loop day of each crypto
                    # day = day_entry
                    if day["top_position"] >= parameters.max_top_position:
                        percent_importance = 0
                    else:
                        percent_importance = day["market_cap"] / day["total_market_cap"] * 100
                    day.update({"percent_importance": percent_importance})

                    theoretical_invest = parameters.starting_usdt_money * percent_importance / 100
                    if not 0 <= theoretical_invest <= 100:
                        assert False

                    day.update({"usdt_invest": theoretical_invest})
                    day.update({"token_owned": theoretical_invest * day["price"]})  # add commission here
                    day_list_of_crypto.update({day["name"]: day})
                    self.storeKeyToDict(daily_wallet_collection, day["name"], day)

                self.check_total_percent_importance_is_equal_to_100(daily_wallet_collection)

            # STEP 2 : RE-BALANCE EACH TURN
            if day_turn > 0:
                base_usdt_money = 0
                sold_money = 0

                # LOOP CAPITAL CALCULATION
                for day_entry in day_list_of_crypto.items():  # Loop day of each crypto
                    day = day_entry[1]

                    if day["top_position"] >= parameters.max_top_position:
                        percent_importance = 0
                    else:
                        percent_importance = day["market_cap"] / day["total_market_cap"] * 100
                    day.update({"percent_importance": percent_importance})

                    # If the day is not in the yesterday list, then we should not have any invested money in it
                    # The capital calculation loop is here only to define the percent importance and
                    # The base_usdt_money just below (but it seems not used for the moment...)
                    last_day = last_day_list_of_crypto[day["name"]]
                    base_usdt_money += day["price"] * last_day["token_owned"]
                    self.storeKeyToDict(daily_wallet_collection, day["name"], day)

                self.check_total_percent_importance_is_equal_to_100(daily_wallet_collection)

                # LOOP RE-BALANCE
                for day_entry in day_list_of_crypto.items():  # Loop day of each crypto
                    day = day_entry[1]

                    if day["top_position"] >= parameters.max_top_position:
                        percent_importance = 0
                    else:
                        percent_importance = day["market_cap"] / day["total_market_cap"] * 100
                    day.update({"percent_importance": percent_importance})

                    last_day = last_day_list_of_crypto[day["name"]]
                    correct_invest = day["percent_importance"] * last_day["token_owned"] * day["price"] / 100

                    if correct_invest > 0 and correct_invest < last_day["usdt_invest"]:
                        # SELL
                        sold_money = correct_invest - last_day["usdt_invest"]
                        last_day["usdt_invest"] = correct_invest  # Are we sure of that ?

                    day.update({"usdt_invest": correct_invest})
                    day.update({"token_owned": correct_invest * day["price"]})  # add commission here

                # TODO loop buy

                # fig.add_trace(
                #     trace=go.Scatter(x=x_list, y=y_list, mode='lines+markers', name=day_list_of_crypto))
            last_day_list_of_crypto = day_list_of_crypto

    def collectingAllDaysInDictionary(self, oldest_crypto, symbol_list, parameters):
        day_turn = -1
        cloud_crypto_points = {}

        for parent_day in oldest_crypto["days"]:  # FOR ALL BITCOIN DAYS
            day_turn += 1
            if day_turn > parameters.ending_day:
                break
            if day_turn < parameters.starting_day:
                continue
            if day_turn % parameters.multiple != 0:
                continue
            for crypto in symbol_list:
                day = self.getDayByDate(crypto, parent_day["date"])
                if day is None:
                    continue
                if day["top_position"] > parameters.max_top_position:
                    continue
                self.storeKeyToDict(cloud_crypto_points, day_turn, {day["name"]: day})
            print("day n°" + str(day_turn))
        return cloud_crypto_points

    def sell_losers(self, last_day, day):  # returns earned usdt money
        # sell x token too much compared to the percent_importance
        column = "percent_importance"
        if day[column] - last_day[column] == 0:
            return 0
        delta = (day[column] - last_day[column]) / last_day[column] * 100
        day
        return 1

    def buy_winners(self, day, base_usdt_money):  # returns ?...

        pass

    def calculateTotalMarketCap(self, symbols, oldest_crypto, parameters):
        turn = -1
        for parent_day in oldest_crypto["days"]:  # FOR ALL BITCOIN DAYS
            turn += 1

            if turn < parameters.starting_day or turn > parameters.ending_day:
                continue

            present_at_this_day = []
            # print("Calculating total market cap for day n°" + str(turn))
            for crypto in symbols:
                if crypto["name"] == "okb":
                    crypto
                for day in crypto["days"]:
                    if day["date"] == parent_day["date"] and day["top_position"] < parameters.max_top_position:
                        present_at_this_day.append(day)
                        break
            total_market_cap = 0
            for day in present_at_this_day:
                total_market_cap += day["market_cap"]
            # print("Total market cap : " + str(total_market_cap / 100000))
            for day in present_at_this_day:
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
