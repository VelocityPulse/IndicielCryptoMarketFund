import requests
import os
import csv

api_key_alphavantage = "T9742OP70MN4QXIG"


data_path = "./data/"
symbols_path = "symbols/"
currency_list = "currency_list"
api_key = api_key_alphavantage


def download_currency_list():
    print("Download currency list")
    currency_list_url = "https://www.alphavantage.co/digital_currency_list/"
    r = requests.get(currency_list_url)

    try:
        os.mkdir(data_path)
    except OSError:
        pass
    finally:
        open(data_path + currency_list, "wb").write(r.content)


def loop_currency_list():
    with open(data_path + currency_list) as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                download_crypto_datas(row[0])
                print(f'\t{row[0]}')
            line_count += 1

        # print(f'Processed {line_count} lines.')


def download_crypto_datas(currency):
    function = "function=" + "DIGITAL_CURRENCY_MONTHLY"
    apikey = "&apikey=" + api_key
    market = "&market=" + "USD"

    symbols = "&symbol=" + currency

    url = "https://www.alphavantage.co/query?" + function + symbols + market + apikey
    # print(url)
    r = requests.get(url)
    data = r.json()
    try:
        os.mkdir(data_path + symbols_path)
    except OSError:
        pass
    finally:
        open(data_path + symbols_path + currency, "wb").write(r.content)

    print(data)


def fetch_data():
    print("Fetch Data")

    download_currency_list()

    loop_currency_list()
