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
		self.stock = None        
		self.NEUTRAL = 0

		#statistical indicator
		self.OVERSOLD = -1
		self.OVERBOUGHT = 1

		#trend direction
		self.DOWNTREND = -1
		self.UPTREND = 1

		#trend strength
		self.WEAK = -1
		self.STRONG =1

		self.BUY = -1
		self.SELL = 1

		self.buythresh = self.BUY * 1
		self.sellthresh = self.SELL * -1

		self.trend_strenght_str = {self.WEAK: "WEAK", self.STRONG: "STRONG"}
		self.trend_dir_str = {self.DOWNTREND: "DOWNTREND", self.NEUTRAL: "NEUTRAL", self.UPTREND: "UPTREND"}
		self.rsi_str = {self.OVERSOLD: "OVERSOLD", self.OVERBOUGHT: "OVERBOUGHT"}
		self.signal_str = {self.BUY: "BUY", self.SELL: "SELL", self.NEUTRAL: "NEUTRAL"}

		self.prevclose = 0
		self.zone = self.NEUTRAL
		self.stop_buyprice = 0
		self.stop_sellprice = 0

		# To keep track of pending orders and buy price/commission
		self.order = None
		self.buyprice = None
		self.buycomm = None

 		# Keep a reference to the "close" line in the data[0] dataseries
		self.dataclose = self.datas[0].close

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
		self.signal = 0
		self.nb_strategies = 0
		self.rsi_vote = 0
		self.cci_vote = 0
		self.stoch_vote = 0
		self.total_vote = 0
		self.signal = self.NEUTRAL

		self.close = self.dataclose[0]
		self.prevclose = self.dataclose[-1]
	
		self.trend_dir = self.__trend_direction(self.close, self.sma20[0], self.sma50[0], self.sma100[0])
		self.trend_str = self.__trend_strength(self.adx[0])
		
		self.rsi_vote = self.__rsi_out_of_band(self.rsi[0])		
		self.nb_strategies += 1
		
		self.cci_vote = self.__cci_out_of_band(self.cci[0])
		self.nb_strategies += 1
		
		self.stoch_vote = self.__stoch_out_of_band(self.stoch[0])
		self.nb_strategies += 1
		
		self.total_vote = self.rsi_vote + self.cci_vote + self.stoch_vote
		self.vote = self.total_vote / self.nb_strategies
	
		# Check if an order is pending ... if yes, we cannot send a 2nd one
		if self.order:
			return

		self.log("NEXT ITERATION...")

		if self.trend_dir is self.DOWNTREND and self.trend_str == self.STRONG and self.vote <= self.buythresh:
			self.signal = self.BUY		
		elif self.trend_dir is self.UPTREND and self.trend_str == self.STRONG and self.vote >= self.sellthresh and self.position:
			self.signal = self.SELL
		else:
			self.signal = self.NEUTRAL
		
		if self.signal == self.BUY:
				self.order = self.buy()
		elif self.signal == self.SELL:
				self.order = self.sell()

		self.log("close %8.3f, prevclose %8.3f, atr %8.3f" % (
				self.close, self.prevclose, self.atr[0]))
		self.log("sma20 %8.3f, sma50 %8.3f, sma100 %8.3f" % (
				self.sma20[0], self.sma50[0], self.sma100[0]))
		self.log("adx %8.3f, rsi %8.3f, cci %8.3f, stoch %8.3f" % (
				self.adx[0], self.rsi[0], self.cci[0], self.stoch[0]))
		self.log("trend_dir %s, trend_str %s, rsi_vote %d, cci_vote %d, stoch_vote %d" % (
				self.trend_dir_str[self.trend_dir], self.trend_strenght_str[self.trend_str], self.rsi_vote, self.cci_vote, self.stoch_vote))
		self.log("vote %.2f, buy thresh %.2f, sell thresh %.2f, signal %s" % (
				self.vote, self.buythresh, self.sellthresh, self.signal_str[self.signal]))


	def __trend_direction(self, close, sma20, sma50, sma100):
		if close is None or sma20 is None or sma50 is None:
			signal = self.NEUTRAL
			self.log("invalid sma values, trend neutral")
		elif close >= sma20 and close >= sma50 and close >= sma100 and sma20 > sma50:
			signal = self.UPTREND
		elif close < sma20 and close < sma50 and close < sma100 and sma20 < sma50:
			signal = self.DOWNTREND
		else:
			signal = self.NEUTRAL

		return signal

	def __trend_strength(self, adx):
		if adx is None:
			signal = self.NEUTRAL
		else:
			if adx < 25:
				signal = self.WEAK
			elif adx > 25:
				signal = self.STRONG
			else:
				signal = self.NEUTRAL

		return signal

	def __rsi_out_of_band(self, rsi):
		if rsi is None:
			signal = self.NEUTRAL
		else:
			if rsi < 30:
				signal = self.OVERSOLD
			elif rsi > 70:
				signal = self.OVERBOUGHT
			else:
				signal = self.NEUTRAL

		return signal

	def __cci_out_of_band(self, cci):
		if cci is None:
			signal = self.NEUTRAL
		else:
			if cci < -100:
				signal = self.OVERSOLD
			elif cci > 100:
				signal = self.OVERBOUGHT
			else:
				signal = self.NEUTRAL

		return signal

	def __stoch_out_of_band(self, stoch):
		if stoch is None:
			signal = self.NEUTRAL
		else:
			if stoch < 30:
				oversold = self.OVERSOLD
				signal = oversold
			elif stoch > 70:
				signal = self.OVERBOUGHT
			else:
				signal = self.NEUTRAL

		return signal

class ZoneIndicator(bt.Indicator):
	lines = ('trend',)

	def __init__(self):		
		self.dataclose = self.datas[0].close
		
		sma20 = bt.indicators.SimpleMovingAverage(
			self.datas[0], period=20)

		sma50 = bt.indicators.SimpleMovingAverage(
			self.datas[0], period=50)

		sma100 = bt.indicators.SimpleMovingAverage(
			self.datas[0], period=100)
		
	def next(self):
		if close is None or sma20 is None or sma50 is None:
			signal = self.NEUTRAL			
		elif close >= sma20 and close >= sma50 and close >= sma100 and sma20 > sma50:
			signal = self.UPTREND
		elif close < sma20 and close < sma50 and close < sma100 and sma20 < sma50:
			signal = self.DOWNTREND
		else:
			signal = self.NEUTRAL

		self.l.trend = signal

if __name__ == '__main__':
	# Create a cerebro entity
	cerebro = bt.Cerebro()

	data = bt.feeds.YahooFinanceData(dataname='NIO', fromdate=datetime(2018, 1, 1), todate=datetime(2020, 7, 1))

	# Add the Data Feed to Cerebro
	cerebro.adddata(data)

	# Add a strategy
	cerebro.addstrategy(TestStrategy)

	# Set our desired cash start
	cerebro.broker.setcash(1000.0)

	# Add a FixedSize sizer according to the stake
	cerebro.addsizer(bt.sizers.AllInSizer)

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