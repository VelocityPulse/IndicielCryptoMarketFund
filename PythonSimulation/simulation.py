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

    def checkDuplicatePosition(self, json_list, day_number):
        days = []

        oldest_crypto = self.find_oldest_crypto(json_list)

        date = oldest_crypto["days"][day_number]["date"]

        for crypto in json_list:
            for day in crypto["days"]:
                if day["date"] == date:
                    days.append(day)

        position_list = []
        for day in days:
            if position_list.__contains__(day["top_position"]):
                print("duplicate top position")
                exit(-1)
            position_list.append(day["top_position"])
        print("success...")

    def checkDuplicatePositionInList(self, check_list):
        present_number = []

        for item in check_list:
            if present_number.__contains__(item):
                return False
            present_number.append(item)
        return True

    def storeToDictionaryForCheck(self, relative_day_count, daily_dictionary_position_check, top_position, crypto):
        new_key = {relative_day_count: top_position}
        if crypto["name"] in daily_dictionary_position_check:
            daily_dictionary_position_check[crypto["name"]].update(new_key)
        else:
            new_row = {crypto["name"]: {}}
            daily_dictionary_position_check.update(new_row)
            daily_dictionary_position_check[crypto["name"]].update(new_key)

    def checkDuplicatePositionByDictionary(self, dictionary, starting_day, max_day):
        duplication_count = 0
        for i in range(starting_day, max_day):
            days_dict = {}
            for crypto in dictionary.items():
                for day in crypto[1]:
                    if i == day:
                        days_dict.update({crypto[0]: crypto[1][day]})

            used_positions = []
            for item in days_dict.items():
                if used_positions.__contains__(item[1]):
                    print("error")
                    duplication_count += 1
                    # exit(-1)
                else:
                    used_positions.append(item[1])

        print("duplication found :" + str(duplication_count))
        pass

    def start(self):
        symbol_list = self.getSymbols()

        self.checkDuplicatePosition(symbol_list, 3304)

        multiple = 1
        stopping_end = 19
        starting_day = 3291
        max_top_position = 90

        fig = go.Figure()
        processed_crypto = []
        oldest_crypto = self.find_oldest_crypto(symbol_list)
        day_turn = 0
        symbol_turn = 0

        daily_dictionary_position_check = {}

        for parent_day in oldest_crypto["days"]:  # FOR ALL BITCOIN DAYS

            for crypto in symbol_list:  # FOR ALL PRESENT CRYPTO IN THIS BITCOIN DAY

                symbol_turn += 1
                if processed_crypto.__contains__(crypto):
                    continue
                x_list = []
                y_list = []
                if crypto["days"][0]["date"] == parent_day["date"]:
                    first_crypto_day = -1

                    for day in crypto["days"]:  # FOR ALL DAYS OF THIS PRESENT CRYPTO
                        first_crypto_day += 1

                        if day["top_position"] == -1:
                            print("passing position " + str(day["top_position"]))
                            continue

                        relative_day_count = day_turn + first_crypto_day

                        if relative_day_count > len(oldest_crypto["days"]) - stopping_end:
                            continue

                        top_position = day["top_position"] + 101 - day["top_position"] * 2

                        if relative_day_count == 3294 and crypto["name"] == "dogecoin":
                            crypto  # date = 1652140800000
                            # market cap  =
                            # top position = 7

                        if relative_day_count == 3294 and crypto["name"] == "terra-luna":
                            crypto  # date = 1651968000000
                            # market cap  = 23535728154
                            # top position = 7

                        if relative_day_count % multiple == 0 and top_position > max_top_position:

                            if relative_day_count > starting_day:
                                self.storeToDictionaryForCheck(relative_day_count, daily_dictionary_position_check,
                                                               top_position, crypto)

                                x_list.append(relative_day_count)
                                y_list.append(top_position)

                    processed_crypto.append(crypto)
                    fig.add_trace(trace=go.Scatter(x=x_list, y=y_list, mode='lines+markers', name=crypto["name"]))

            day_turn += 1
            print("day n°" + str(day_turn))
        self.checkDuplicatePositionByDictionary(daily_dictionary_position_check, starting_day, day_turn)
        fig.show()

        pass
