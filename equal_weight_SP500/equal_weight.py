import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math

#import index data from api

stocks = pd.read_csv('../sp_500_stocks.csv')

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

def chunks(arr, n):
    for i in range(0,len(arr), n):
        yield(arr[i:i + n])

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []

for i in range(len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

final_dataframe = pd.DataFrame(columns = cols)

for symbol_str in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_str.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series(
                [symbol,
                data[symbol]['quote']['latestPrice'],
                data[symbol]['quote']['marketCap'],
                'N/A'],
                index = cols
            ),
            columns = cols
        )

portfolio_size = input('Please enter the size of your portfolio: ')

try:
    val = float(portfolio_size)
except ValueError:
    print("Try again!")
    portfolio_size = input("Please enter the size of your portfolio: ")

pos_size = float(portfolio_size) / len(final_dataframe)
for i in range(0, len(final_dataframe['Ticker'])-1):
    final_dataframe.loc[i, 'Shares to buy: '] = math.floor(pos_size / final_dataframe['Price'[i]])

write = pd.ExcelWriter('recommended_trades.xlsx', engine='xlsxwriter')
final_dataframe.to_excel(write, sheet_name= 'Recommended Trades', index = False)

background_color = '#FFFFFF'
font_color = "#000000"

str_format = write.book.add_format(
    {
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : 1
    }
)
dollar_format = write.book.add_format(
    {
        'num_format' : '$0.00',
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : 1
    }
)

integer_format = write.book.add_format(
    {
        'num_format' : '0',
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : 1
    }
)

col_formats = {
    'A' : ['Ticker', str_format],
    'B' : ['Price', dollar_format],
    'C' : ['Market Cap', dollar_format],
    'D' : ['Shares to buy', integer_format]
}

for col in col_formats.keys():
    write.sheets['Recommended Trades'].set_column(f'{col}:{col}', 20, col_formats[col][1])
    write.sheets['Recommended Trades'].write(f'{col}1', col_formats[col][0], str_format)

write.save()

