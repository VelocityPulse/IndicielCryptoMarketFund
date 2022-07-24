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

        oldest_crypto = self.find_oldest_crypto(symbol_list)
        self.calculate_total_market_cap(symbol_list, oldest_crypto, parameters)

        # Cloud crypto points is a dictionary where each key is a day index that contains a list of
        # the day of each present crypto at this moment
        cloud_crypto_points = self.collectingAllDaysInDictionary(oldest_crypto, symbol_list, parameters)

        # Process backtesting
        available_and_invested_money = parameters.starting_usdt_money
        last_day_list_of_crypto = {}
        day_turn = -1
        wallet = {}
        for day_list_of_crypto in cloud_crypto_points.values():  # Loop all days
            day_turn += 1

            # LOOP CALCULATE THE PERCENT IMPORTANCE (By using total market cap including parameters rules)
            for day_entry in day_list_of_crypto.items():  # Loop day of each crypto
                day = day_entry[1]

                if day["top_position"] >= parameters.max_top_position:
                    percent_importance = 0
                else:
                    percent_importance = day["market_cap"] / day["total_market_cap"] * 100

                day.update({"percent_importance": percent_importance})

            self.check_total_percent_importance_is_equal_to_100(day_list_of_crypto)

            # LOOP CALCULATE AVAILABLE MONEY
            # Here we do not reset available_and_invested_money to 0 because the first turn it will not be
            # added anyway, Wallet is empty.
            # It should be reset to 0 at the sell/buy step
            for crypto in wallet:  # Loop day of each crypto

                # TODO : I think the access of this dict is wrong
                if crypto["name"] in day_list_of_crypto:
                    day = day_list_of_crypto[crypto["name"]]
                    available_and_invested_money += crypto["owned_token"] * day["price"]

            for day_entry in day_list_of_crypto.items():
                day = day_entry[1]

                # TODO : calculate ideal repartition



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

    @staticmethod
    def calculate_total_market_cap(symbols, oldest_crypto, parameters):
        turn = -1
        for parent_day in oldest_crypto["days"]:  # FOR ALL BITCOIN DAYS
            turn += 1

            if turn < parameters.starting_day or turn > parameters.ending_day:
                continue

            present_at_this_day = []
            for crypto in symbols:
                for day in crypto["days"]:
                    if day["date"] == parent_day["date"] and day["top_position"] < parameters.max_top_position:
                        present_at_this_day.append(day)
                        break
            total_market_cap = 0
            for day in present_at_this_day:
                total_market_cap += day["market_cap"]
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
