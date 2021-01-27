import numpy as np
import pandas as pd
import xlsxwriter
import math
from scipy import stats
import requests

stocks = pd.read_csv("../sp_500_stocks.csv")
from secrets import IEX_CLOUD_API_TOKEN

symbol = 'GOOG'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + 1]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

my_columns = ['Ticker', 'Price', 'Price-to-Earnings Ratio', 'Number of Shares to Buy']

final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
#     print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
                                        pd.Series([symbol, 
                                                   data[symbol]['quote']['latestPrice'],
                                                   data[symbol]['quote']['peRatio'],
                                                   'N/A'
                                                   ], 
                                                  index = my_columns), 
                                        ignore_index = True)

final_dataframe.sort_values('Price-to-Earnings Ratio', inplace = True)
final_dataframe = final_dataframe[final_dataframe['Price-to-Earnings Ratio'] > 0]
final_dataframe = final_dataframe[:50]
final_dataframe.reset_index(inplace = True)
final_dataframe.drop('index', axis=1, inplace = True)

def p_input():
    psize = input("Enter the value of portfolio: ")
    try:
        val = float(psize)
    except ValueError:
        print("Invalid entry")
        psize = input("Enter value of portfolio")
    return float(psize)

p_size = p_input()
pos_size = p_size/len(final_dataframe)
for i in range(len(final_dataframe['Ticker'])):
    final_dataframe.loc[i, 'Shares to Buy'] = math.floor(pos_size /final_dataframe['Price'][i])

