import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math

#import index data from api

stocks = pd.read_csv('sp_500_stocks.csv')
#stocks #if run on ipynb

#acquire api token

from secrets import IEX_CLOUD_API_TOKEN

symbols = ['AAPL', 'GOOG']
data = []
prices = {}
market_caps = {}
cols = [ 'Ticker', 'Stock Price', 'Market Cap', 'Number of Shares to buy']
out_dataframe = pd.DataFrame(columns = cols)
for symbol in symbols:
    api_url = 'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
    info = requests.get(api_url).json()
    print(data.status_code == 200)
    data.append(info)
    prices[symbol] = info['latestPrice']
    market_caps[symbol] = info['marketCap']

    out_dataframe = out_dataframe.append(
        pd.Series(
            [
                symbol,
                info['latestPrice'],
                info['marketCap'],
                'N/A'
            ],
            index = cols
        ),
        ignore_index = True
    )



out_dataframe.append(
    pd.Series(
        [
            symbol,
            prices[symbol],
            market_caps[symbol],
            'N/A'
        ],
        index = cols
    ),
    ignore_index = True
)
