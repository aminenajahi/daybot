from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds

# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma20 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=20)

        self.sma50 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=50)

        self.sma100 = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=100)
        
        self.cci = bt.indicators.CommodityChannelIndex(self.datas[0])
        self.stoch = bt.indicators.StochasticSlow(self.datas[0])
        self.rsi = bt.indicators.RSI(self.datas[0])
        self.atr = bt.indicators.ATR(self.datas[0])
        self.adx = bt.talib.ADX(self.data.high, self.data.low, self.data.close)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()


    #data = btfeeds.GenericCSVData(
    #    dataname='feeds/RCL.csv',
    #    fromdate=datetime(2019, 1, 1),
    #    todate=datetime(2020, 7, 1),
    #    nullvalue=0.0,
    #    dtformat=('%Y-%m-%d'),
    #    datetime=0,
    #    high=1,
    #    low=2,
    #    open=3,
    #    close=4,
    #    volume=5,
    #    openinterest=-1
    #)

    data = bt.feeds.YahooFinanceData(dataname='AAPL', fromdate=datetime(2019, 1, 1), todate=datetime(2020, 6, 1))

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Set our desired cash start
    cerebro.broker.setcash(1000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()