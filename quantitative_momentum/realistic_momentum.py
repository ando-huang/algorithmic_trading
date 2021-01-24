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
        hqm_dataframe.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(hqm_dataframe[f'{time_period} Price Return'],
                hqm_dataframe.loc[row, f'{time_period} price Return'])/100

from statistics import mean

for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} Return Percentile'])
    hqm_dataframe.loc[row, 'HQM Score'] = mean(momentum_percentiles)

#sort and select best 50
hqm_dataframe.sort_values(by = 'HQM Score', ascending = False)
hqm_dataframe = hqm_dataframe[:51]

#calculate how many to buy
p_size = portfolio_input()

position_size = float(p_size)/len(hqm_dataframe.index)
for index in range(len(hqm_dataframe['Ticker'])-1):
    hqm_dataframe.loc[index, 'Number of Shares to Buy'] = math.floor(position_size / hqm_dataframe['Price'][index])

writer = pd.ExcelWriter('momentum_strategy.xlsx', engine='xlsxwriter')
hqm_dataframe.to_excel(writer, sheet_name='Momentum Strategy', index = False)

background_color = '#0a0a23'
font_color = '#ffffff'

string_template = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

dollar_template = writer.book.add_format(
        {
            'num_format':'$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

integer_template = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

percent_template = writer.book.add_format(
        {
            'num_format':'0.0%',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

column_formats = {
                    'A': ['Ticker', string_template],
                    'B': ['Price', dollar_template],
                    'C': ['Number of Shares to Buy', integer_template],
                    'D': ['One-Year Price Return', percent_template],
                    'E': ['One-Year Return Percentile', percent_template],
                    'F': ['Six-Month Price Return', percent_template],
                    'G': ['Six-Month Return Percentile', percent_template],
                    'H': ['Three-Month Price Return', percent_template],
                    'I': ['Three-Month Return Percentile', percent_template],
                    'J': ['One-Month Price Return', percent_template],
                    'K': ['One-Month Return Percentile', percent_template],
                    'L': ['HQM Score', integer_template]
                    }

for column in column_formats.keys():
    writer.sheets['Momentum Strategy'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Momentum Strategy'].write(f'{column}1', column_formats[column][0], string_template)

writer.save()