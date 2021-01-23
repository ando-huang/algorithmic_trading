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