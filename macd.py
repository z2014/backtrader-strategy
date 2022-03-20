import datetime
import os.path
import sys
import backtrader as bt
import talib
import numpy as np 
import matplotlib
import math
import pandas as pd

fastperiod = 12
slowperiod = 26
signalperiod = 9
class MACDStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        # bt.indicators.MACDHisto(self.datas[0], period_me1=fastperiod, period_me2=slowperiod, period_signal=signalperiod)
        bt.indicators.SMA(self.datas[0], period=13)

    def notify_order(self, order):
        # 前一天下单，以后一天的价格成交
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

        self.order = None

    def next(self):
        close = np.array(self.dataclose.get(ago=0, size=self.__len__()))
        macd, macdsignal, macdhist = talib.MACD(close, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        ma13 = talib.MA(close, timeperiod=13)
        
        if self.order:
            return

        if not self.position:
            # if macdhist[-1] > 0 and macd[-1] > 0:
            if close[-1] > ma13[-1]:
                self.order = self.buy()

        else:
            # if macdhist[-1] < 0 and macd[-1] < 0:
            if close[-1] < ma13[-1]:
                self.order = self.sell()

class FixedSize(bt.Sizer):
 
    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)

        if isbuy:
            return math.floor(cash/data.open)

        return position.size

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(MACDStrategy)
    cerebro.addsizer(FixedSize)

    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, './datas/0700.HK.csv')

    # 加载提前从雅虎金融下载的股价
    # data = bt.feeds.YahooFinanceCSVData(
    #     dataname=datapath,
    #     fromdate=datetime.datetime(2022, 1, 1, 10, 0, 0),
    #     todate=datetime.datetime(2022, 1, 28, 16, 0, 0),
    #     reverse=False)

    dataframe = pd.read_csv('./datas/0700.HK.csv', index_col=0, parse_dates=True)
    data = bt.feeds.PandasData(
        dataname=dataframe,
        fromdate=datetime.datetime(2021, 1, 1),
        todate=datetime.datetime(2022, 3, 4),
        timeframe=bt.TimeFrame.Minutes
        )
        
    # timeframe=bt.TimeFrame.Minutes
    cerebro.adddata(data)

    # 设置初始现金
    cerebro.broker.setcash(100000.0)

    # 设置佣金
    cerebro.broker.setcommission(commission=0.001)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()