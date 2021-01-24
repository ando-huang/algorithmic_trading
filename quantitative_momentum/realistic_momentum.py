import numpy as np
import pandas as pd
import requests
import xlsxwriter as xlsx
import math
from scipy import stats

stocks = pd.read_csv('../sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN

test = 'GOOG'
api_url = f'https://sandbox.iexapis.com/stable/stock/{test}/stats?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()

def chunks(arr, step):
    for index in range(0, len(arr), step):
        yield(arr[index:index + step])

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strs = []
for index in range(len(symbol_groups)):
    symbol_strs.append(','.join(symbol_groups[index]))

def portfolio_input():
    v = 1
    while v == 1:
        portfolio_size = input("Enter the value of your portfolio: ")
        try:
            value = float(portfolio_size)
            return value
        except:
            print("Invalid input!")
            portfolio_size = input("Enter the value of your portfolio: ")

p_input = portfolio_input()

hqm_cols = [
    'Ticker'
    'Price', 
    'Number of Shares to Buy', 
    'One-Year Price Return', 
    'One-Year Return Percentile',
    'Six-Month Price Return',
    'Six-Month Return Percentile',
    'Three-Month Price Return',
    'Three-Month Return Percentile',
    'One-Month Price Return',
    'One-Month Return Percentile',
    'HQM Score'
]
hqm_dataframe = pd.DataFrame(columns = hqm_cols)

for symbol_str in symbol_strs:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_str}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_str.split(','):
        hqm_dataframe = hqm_dataframe.append(
            pd.Series([symbol,
                data[symbol]['quote']['latestPrice'],
                'N/A',
                data[symbol]['stats']['year1ChangePercent'],
                'N/A',
                data[symbol]['stats']['month6ChangePercent'],
                'N/A',
                data[symbol]['stats']['month3ChangePercent'],
                'N/A',
                data[symbol]['stats']['month1ChangePercent'],
                'N/A',
                'N/A'
                ],
            index = hqm_cols
            ),
        ignore_index = True
        )

time_periods = [
        'One-Year',
        'Six-Month',
        'Three-Month',
        'One-Month'
        ]

for row in hqm_dataframe.index:
    for time_period in time_periods:
        hqm_dataframe.loc[row, f'{time_period} return Percentile']
        = stats.percentileofscore(hqm_dataframe[f'{time_period} Price Return'],
                hqm_dataframe.loc[row, f'{time_period} price Return'])/100

from statistics import mean

for row in hqm_dataframe.index:
    momentum_percentiles = []

