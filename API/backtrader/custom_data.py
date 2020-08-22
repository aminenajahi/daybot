from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds

class SmaCross(bt.SignalStrategy):
    params = (('pfast', 10), ('pslow', 30),)

    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=self.p.pfast), bt.ind.SMA(period=self.p.pslow)
        self.signal_add(bt.SIGNAL_LONG, bt.ind.CrossOver(sma1, sma2))


cerebro = bt.Cerebro()

data = btfeeds.GenericCSVData(
    dataname='feeds/NIO.csv',
    #dataname='feeds/sin.csv',

    fromdate=datetime(2020, 1, 1),
    todate=datetime(2020, 7, 1),

    nullvalue=0.0,

    dtformat=('%Y-%m-%d'),

    datetime=0,
    close=4,
)

cerebro.adddata(data)
cerebro.addstrategy(SmaCross)
cerebro.run()
cerebro.plot()