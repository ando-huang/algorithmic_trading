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

my_cols = ['Ticker', 'Price', 'One-Year Price Return', 'Shares to Buy']

final_dataframe = pd.DataFrame(columns = my_cols)
for symbol_str in symbol_strs:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/{symbol_str}/stats?token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_str.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series([
                symbol,
                data[symbol]['quote']['latestPrice'],
                data[symbol]['stats']['year1ChangePercent'],
                'N/A'
            ],
            index = my_cols
            ),
            ignore_index = True
        )

final_dataframe.sort_values('One-Year Price Return', ascending = False, inplace = True)
final_dataframe = final_dataframe[:51]
final_dataframe.reste_index(drop = True, inplace = True)

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

p_size = float(p_input)/len(final_dataframe.index)
for index in range(len(final_dataframe['Ticker'])):
    final_dataframe.loc[index, 'Shares to Buy'] = math.floor(p_size / final_dataframe['Price'][index])

