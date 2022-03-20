from futu import *
import talib
import numpy as np 
import matplotlib.pyplot as plt
import backtrader as bt
import datetime
import pandas as pd


date = []
open = []
high = []
low = []
close = []
Adj_Close = []
volume = []


quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)  # 创建行情对象
ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', start='2021-01-01', end='2022-03-04', ktype=KLType.K_30M, max_count=50)  # 每页40个，请求第一页
if ret == RET_OK:
    close = close + data['close'].values.tolist()
    Adj_Close = Adj_Close + data['close'].values.tolist()
    date = date + data['time_key'].values.tolist()
    open = open + data['open'].values.tolist()
    high = high + data['high'].values.tolist()
    low = low + data['low'].values.tolist()
    volume = volume + data['volume'].values.tolist()
else:
    print('error:', data)

while page_req_key != None:  # 请求后面的所有结果
    ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', start='2021-01-01', end='2022-03-04',ktype=KLType.K_30M, max_count=50, page_req_key=page_req_key) # 请求翻页后的数据
    if ret == RET_OK:
        close = close + data['close'].values.tolist()
        date = date + data['time_key'].values.tolist()
        open = open + data['open'].values.tolist()
        high = high + data['high'].values.tolist()
        low = low + data['low'].values.tolist()
        volume = volume + data['volume'].values.tolist()
        Adj_Close = Adj_Close + data['close'].values.tolist()
    else:
        print('error:', data)

quote_ctx.close()

data_frame = pd.DataFrame({ 'Date': date, 'Close': close, 'Open': open,  'High': high, 'Low': low, 'Adj Close': Adj_Close, 'Volume':volume })
data_frame.to_csv('test.csv', index=False, sep=',')


# macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)