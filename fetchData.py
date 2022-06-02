import json
import os
import time

import requests


class FetchData:
    data_path = "./data/"
    symbols_path = "symbols/"
    currency_list = "currency_list"
    order_id = 1

    @classmethod
    def request_get(cls, url):
        r = requests.get(url)
        while r.status_code != 200:
            print("error code : " + str(r.status_code) + " WAITING DELAY")
            time.sleep(5)
            r = requests.get(url)
        return r

    @classmethod
    def download_currency_list(cls):
        print("Download currency list")
        address = "https://api.coingecko.com/api/v3/coins/markets"
        param1 = "?vs_currency=usd&"
        param2 = "order=market_cap_desc&"
        param3 = "include_platform=false"
        currency_list_url = address + param1 + param2 + param3
        r = cls.request_get(currency_list_url)

        try:
            os.mkdir(cls.data_path)
        except OSError:
            pass
        finally:
            open(cls.data_path + cls.currency_list, "wb").write(r.content)

    @classmethod
    def loop_currency_list(cls):
        file = open(cls.data_path + cls.currency_list)
        json_list = json.loads(file.read())

        for i in json_list:
            cls.download_crypto_datas(currency=i['id'])

        # print(f'Processed {line_count} lines.')

    @classmethod
    def download_crypto_datas(cls, currency):
        param1 = "vs_currency=usd&"
        param2 = "days=max&"
        param3 = "interval=daily&"

        url = "https://api.coingecko.com/api/v3/coins/" + currency + "/market_chart/?" + param1 + param2 + param3
        print(url)

        r = cls.request_get(url)

        try:
            os.mkdir(cls.data_path + cls.symbols_path)
        except OSError:
            pass
        finally:
            # filter interval to monthly
            open(cls.data_path + cls.symbols_path + str(cls.order_id) + "_" + currency, "wb").write(r.content)

        cls.order_id += 1
        print(r.content)

    @classmethod
    def fetch_data(cls):
        print("Fetch Data")

        cls.download_currency_list()

        cls.loop_currency_list()
