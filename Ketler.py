""""
Ketler Channel
"""

import backtrader as bt
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import backtrader.analyzers as btanalyzers
import talib


class Ketler(bt.Indicator):
    params = dict(ema=20, atr=17)
    lines = ()
    plotinfo = dict(subplot=False)
    plotlines = dict(
        upper=dict(ls='--'),
        lower=dict(_samecolor=True),
    )

    def __init__(self):
        self.l.expo = talib.EMA(self.datas[0].close, timeperiod=self.params.ema)
        self.l.atr = talib.ATR(self.data.high, self.data.low, self.data.close,  timeperiod=self.params.atr)


class Strategy(bt.Strategy):
    ''' Logging function for strategy'''

    def log(self, txt, dt=None):
        print(f"{dt.isoformat()}, {txt}")

    def __init__(self):
        pass

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

        self.log("OPERATION PROFIT, GROSS %.2F, NET %.2F" % (trade.pnl, trade.pnlcomm))

    def next(self):
        pass


if __name__ == "__main__":
    cerebro = bt.Cerebro()
    data = bt.feeds.YahooFinanceData(
        dataname="AAPL",
        fromdate=datetime.datetime(2015, 1, 1),
        todate=datetime.datetime(2020, 12, 31),
        timeframe=bt.TimeFrame.Days,
    )
    cerebro.adddata(data)
    cerebro.addstrategy(Strategy)
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=98)

    print("Start Portfolio Value {}".format(cerebro.broker.get_value()))
    back = cerebro.run()
    print("end portfolio value {}".format(cerebro.broker.get_value()))

    cerebro.plot(style="candle")
