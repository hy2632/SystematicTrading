""""
Ketler Channel
"""

import backtrader as bt
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import backtrader.analyzers as btanalyzers
import talib
import time
import pdb


class Ketler(bt.Indicator):
    params = dict(ema=20, atr=17)
    lines = ("expo", "atr", "upper", "lower")  # Define the four lines
    plotinfo = dict(subplot=False)
    plotlines = dict(
        upper=dict(ls='--'),
        lower=dict(_samecolor=True),
    )

    def __init__(self):
        self.l.expo = bt.talib.EMA(self.datas[0].close, timeperiod=self.params.ema)
        self.l.atr = bt.talib.ATR(self.data.high, self.data.low, self.data.close, timeperiod=self.params.atr)
        self.l.upper = self.l.expo + self.l.atr
        self.l.lower = self.l.expo - self.l.atr


class Strategy(bt.Strategy):
    ''' Logging function for strategy'''

    def log(self, txt, dt=None):
        print(f"{dt.isoformat()}, {txt}")

    def __init__(self):
        self.ketler = Ketler()
        self.close = self.data.close

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted by broker, nothing to do
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: {:.2%f}, Cost: {:.2%f}, Comm {:.2%f}".format(
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm,
                    )
                )
            else:
                self.log(
                    "SELL EXECUTED, Price: {:.2%f}, Cost: {:.2%f}, Comm {:.2%f}".format(
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm,
                    )
                )
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))

    def next(self):
        """ Apply the Ketler Strategy """
        if not self.position:
            if self.close[0] > self.ketler.upper[0]:
                self.order = self.order_target_percent(target=0.95)
        else:
            if self.close[0] < self.ketler.expo[0]:
                self.order = self.sell()


if __name__ == "__main__":
    cerebro = bt.Cerebro()

    start_time = time.time()
    print("Loading Data from Yahoo Finance ...")

    data = bt.feeds.YahooFinanceData(
        dataname="AAPL",
        fromdate=datetime.datetime(2015, 1, 1),
        todate=datetime.datetime(2020, 12, 14),
        timeframe=bt.TimeFrame.Days,
    )

    end_time = time.time()
    print("Data Loaded.")

    cerebro.adddata(data)
    cerebro.addstrategy(Strategy)
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=98)

    print("Start Portfolio Value {}".format(cerebro.broker.get_value()))
    back = cerebro.run()
    print("end portfolio value {}".format(cerebro.broker.get_value()))

    cerebro.plot(style="candle")
