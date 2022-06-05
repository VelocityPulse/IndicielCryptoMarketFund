import json
import os
import shutil
import sys
import time

import requests


class FetchData:
    data_path = "./data/"
    symbols_path = "symbols/"
    currency_list = "currency_list"
    stable_coins = ["busd", "usdt", "usdc", "dai", "tusd", "usdp", "usdn", "usdd", "fei"]
    additional_coin = ["terra-luna"]

    def __init__(self):
        pass

    @staticmethod
    def request_get(url):
        r = requests.get(url)
        while r.status_code != 200:
            print("error code : " + str(r.status_code) + " WAITING DELAY")
            time.sleep(5)
            r = requests.get(url)
        return r

    def download_currency_list(self):
        print("Download currency list")
        address = "https://api.coingecko.com/api/v3/coins/markets"
        param1 = "?vs_currency=usd&"
        param2 = "order=market_cap_desc&"
        param3 = "include_platform=false"
        currency_list_url = address + param1 + param2 + param3
        r = self.request_get(currency_list_url)

        try:
            os.mkdir(self.data_path)
        except OSError:
            pass
        finally:
            open(self.data_path + self.currency_list, "wb").write(r.content)

    def loop_currency_list(self):
        file = open(self.data_path + self.currency_list)
        json_list = json.loads(file.read())

        for i in json_list:
            if i['symbol'] in self.stable_coins:
                continue
            self.download_crypto_datas(currency=i['id'])

        for i in self.additional_coin:
            self.download_crypto_datas(currency=i)

    def download_crypto_datas(self, currency):
        param1 = "vs_currency=usd&"
        param2 = "days=max&"
        param3 = "interval=daily&"

        url = "https://api.coingecko.com/api/v3/coins/" + currency + "/market_chart/?" + param1 + param2 + param3
        print(url)

        r = self.request_get(url)

        try:
            os.mkdir(self.data_path + self.symbols_path)
        except OSError:
            pass
        finally:
            # filter interval to monthly
            purified = self.purify_json(r.content, currency)
            # purified = r.content
            open(self.data_path + self.symbols_path + currency, "wb").write(purified)

        # print(r.content)

    @staticmethod
    def test_json_purified(crypto):
        for day in crypto["days"]:
            if day["market_cap"] is None:
                assert False

    def purify_json(self, content, currency):
        j = json.loads(content)

        j["name"] = currency

        del j["total_volumes"]

        j["days"] = []
        for i in range(0, len(j["prices"])):
            new_values = dict()
            new_values["date"] = j["prices"][i][0]
            new_values["price"] = j["prices"][i][1]
            new_values["market_cap"] = j["market_caps"][i][1]
            if new_values["market_cap"] is None:
                new_values["market_cap"] = j["market_caps"][i - 1][1]
            new_values["top_position"] = -1
            new_values["name"] = currency
            j["days"].append(new_values)

        del j["prices"]
        del j["market_caps"]

        # Change single quote to double quotes
        self.test_json_purified(j)
        j = json.dumps(j)
        return bytearray(str(j).encode())

    @staticmethod
    def find_oldest_crypto(json_list):
        ret = 0
        time_ref = sys.maxsize

        for crypto in json_list:
            if crypto["days"][0]["date"] < time_ref:
                time_ref = crypto["days"][0]["date"]
                ret = crypto
        return ret

    @staticmethod
    def testTopIsSorted(days):
        market_cap = 0.0

        for day in days:
            try:
                if market_cap < day["market_cap"]:
                    market_cap = day["market_cap"]
            except TypeError as e:
                print(e)
            try:
                assert market_cap >= day["market_cap"]
            except AssertionError as e:
                print(e)

    @staticmethod
    def get_day_date(elem):
        return elem["date"]

    @staticmethod
    def find_crypto(json_list, currency):
        for i in json_list:
            if i["name"] == currency:
                return i
        return None

    def calculate_top_positions(self):
        t = time.time()
        print("Calculate top position")
        json_list = []

        for file in os.listdir(self.data_path + self.symbols_path):
            with open(self.data_path + self.symbols_path + file, "r") as f:
                json_list.append(json.loads(f.read()))

        oldest_crypto = self.find_oldest_crypto(json_list)

        turn = 0
        for parent_day in oldest_crypto["days"]:
            present_at_this_date = []
            for crypto in json_list:
                for i in crypto["days"]:
                    if i["date"] > parent_day["date"]:
                        break
                    if i["date"] == parent_day["date"]:
                        present_at_this_date.append(i)
                        continue

            present_at_this_date.sort(key=self.get_day_date)
            self.testTopIsSorted(present_at_this_date)

            for position in range(0, len(present_at_this_date)):
                crypto = self.find_crypto(json_list, present_at_this_date[position]["name"])
                for day in crypto["days"]:
                    if day["date"] == parent_day["date"]:
                        day["top_position"] = position + 1
                        continue

            print("day n°" + str(turn))
            turn += 1

        print("End. Time : " + str((time.time() - t)))
        pass

    def fetch_data(self):
        print("Fetch Data")

        shutil.rmtree(self.data_path)

        self.download_currency_list()

        self.loop_currency_list()
