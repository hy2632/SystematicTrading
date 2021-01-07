import pdb
import backtrader as bt
import datetime
import pandas as pd


class Strategy(bt.Strategy):
    ''' Logging function for strategy'''
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")

    def __init__(self):
        self.close = self.data.close

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted by broker, nothing to do
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f"BUY EXECUTED, Price: {order.executed.price: .2f}, Cost: {order.executed.value: .2f}, Comm: {order.executed.comm: .2f}"
                )
            else:
                self.log(
                    f"SELL EXECUTED, Price: {order.executed.price: .2f}, Cost: {order.executed.value: .2f}, Comm: {order.executed.comm: .2f}"
                )
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        """ Do Nothing if in position """
        if not self.position:
            self.order = self.order_target_percent(target=0.95)
        else:
            pass


if __name__ == "__main__":
    cerebro = bt.Cerebro()

    data = bt.feeds.YahooFinanceData(
        dataname="AAPL",
        fromdate=datetime.datetime(2015, 1, 1),
        todate=datetime.datetime(2020, 12, 14),
        timeframe=bt.TimeFrame.Days,
    )

    cerebro.adddata(data)
    cerebro.addstrategy(Strategy)
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=98)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")

    print("Start Portfolio Value {}".format(cerebro.broker.get_value()))
    back = cerebro.run()
    print("end portfolio value {}".format(cerebro.broker.get_value()))

    par_list = [[
        x.analyzers.returns.get_analysis()["rtot"],
        x.analyzers.returns.get_analysis()["rnorm100"],
        x.analyzers.drawdown.get_analysis()["max"]["drawdown"],
        x.analyzers.sharpe.get_analysis()["sharperatio"],
    ] for x in back]

    par_df = pd.DataFrame(
        par_list, columns=["Total Return", "APR", "Drawdown", "SharpeRatio"])
    print(par_df)

    cerebro.plot(style="candle")