import json
import os
import shutil
import time

import requests


class FetchData:
    data_path = "./data/"
    symbols_path = "symbols/"
    currency_list = "currency_list"
    order_id = 1
    stable_coins = ["busd", "usdt", "usdc", "dai", "tusd", "usdp", "usdn", "usdd", "fei"]

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

        # print(f'Processed {line_count} lines.')

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
            purified = self.purify_json(r.content)
            # purified = r.content
            open(self.data_path + self.symbols_path + str(self.order_id) + "_" + currency, "wb").write(purified)

        self.order_id += 1
        # print(r.content)

    @staticmethod
    def purify_json(content):
        j = json.loads(content)

        del j["total_volumes"]

        for i in range(0, len(j["prices"])):
            j["prices"][i][0] = j["market_caps"][i][0]

        del j["market_caps"]

        # Change single quote to double quotes
        j = json.dumps(j)
        return bytearray(str(j).encode())

    def fetch_data(self):
        print("Fetch Data")

        shutil.rmtree(self.data_path)

        self.download_currency_list()

        self.loop_currency_list()
