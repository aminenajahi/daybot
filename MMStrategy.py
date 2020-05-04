import math
import talib

class MMStrategy():

	def __init__(self, mylogger):
		self.stock = None
		self.mylogger = mylogger
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

		self.buythresh = self.BUY * 0.5
		self.sellthresh = self.SELL * 0.5

		self.trend_strenght_str = {self.WEAK: "WEAK", self.STRONG: "STRONG"}
		self.trend_dir_str = {self.DOWNTREND: "DOWNTREND", self.NEUTRAL: "NEUTRAL", self.UPTREND: "UPTREND"}
		self.rsi_str = {self.OVERSOLD: "OVERSOLD", self.OVERBOUGHT: "OVERBOUGHT"}
		self.signal_str = {self.BUY: "BUY", self.SELL: "SELL", self.NEUTRAL: "NEUTRAL"}

	def __trend_direction(self, close, sma20, sma50, sma100):
		if close is None or sma20 is None or sma50 is None:
			signal = self.NEUTRAL
		elif close >= sma20 and close >= sma50 and close >= sma100:
			signal = self.UPTREND
		elif close < sma20 and close < sma50 and close < sma100:
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
				signal = self.OVERSOLD
			elif stoch > 70:
				signal = self.OVERBOUGHT
			else:
				signal = self.NEUTRAL

		return signal

	def __print_data(self):
		self.mylogger.logger.debug("%s [%s] positions %d, avg_price %8.3f, close %8.3f, change %8.2f%%, volume %8d" % (
				self.tstamp, self.stock.symbol, self.stock.totalbuysize, self.avgprice, self.close, self.stock.change, self.volume))
		self.mylogger.logger.debug("%s [%s] adx %8.3f, sma20 %8.3f, sma50 %8.3f, sma100 %8.3f " % (
				self.tstamp, self.stock.symbol, self.adx, self.sma20, self.sma50, self.sma100))
		self.mylogger.logger.debug("%s [%s] rsi %8.3f, cci %8.3f, stoch %8.3f " % (
				self.tstamp, self.stock.symbol, self.rsi, self.cci, self.stoch))
		self.mylogger.logger.debug("%s [%s] doji %d,  hammer: %d, eveningstar %d, handingmand %d, shootingstar %d " % (
				self.tstamp, self.stock.symbol, self.doji, self.hammer, self.eveningstar, self.hangingman, self.shootingstar))

	def __print_vote(self):
		self.mylogger.logger.debug("%s [%s] trend_dir %s, trend_str %s, rsi_vote %d, cci_vote %d, stoch_vote %d" % (
				self.tstamp, self.stock.symbol, self.trend_dir_str[self.trend_dir], self.trend_strenght_str[self.trend_str], self.rsi_vote, self.cci_vote, self.stoch_vote))

	def __print_signal(self):
		self.mylogger.logger.debug("%s [%s] vote %.2f, buy thresh %.2f, sell thresh %.2f, signal %s" % (
				self.tstamp, self.stock.symbol, self.vote, self.buythresh, self.sellthresh, self.signal_str[self.signal]))

		if self.signal == self.BUY:
			signal_str = "BUY"
		elif self.signal == self.SELL:
			signal_str = "SELL"
		else:
			signal_str = "NEUTRAL"

		self.mylogger.logger.debug("%s [%s] SIGNAL: %s" % (
				self.tstamp, self.stock.symbol, signal_str))

	def run_strategy(self, tstamp, row, stock):
		self.stock = stock
		self.tstamp = tstamp
		self.close = row['4. close']
		self.volume = row['5. volume']
		self.rsi = row['momentum_rsi']
		self.cci = row['trend_cci']
		self.stoch = row['momentum_stoch_signal']
		self.sma20 = row['sma20']
		self.sma50 = row['sma50']
		self.sma100 = row['sma100']
		self.adx = row['trend_adx']
		self.doji = row['CDLDOJI']
		self.hammer = row['CDLHAMMER']
		self.eveningstar = row['CDLEVENINGSTAR']
		self.hangingman = row['CDLHANGINGMAN']
		self.shootingstar = row['CDLSHOOTINGSTAR']
		self.avgprice = self.stock.avgbuyprice

		self.signal = 0
		self.nb_strategies = 0
		self.rsi_vote = 0
		self.cci_vote = 0
		self.stoch_vote = 0
		self.total_vote = 0

		self.trend_dir = self.__trend_direction(self.close, self.sma20, self.sma50, self.sma100)
		self.trend_str = self.__trend_strength(self.adx)

		self.rsi_vote = self.__rsi_out_of_band(self.rsi)
		self.nb_strategies += 1

		self.cci_vote = self.__cci_out_of_band(self.cci)
		self.nb_strategies += 1

		self.stoch_vote = self.__stoch_out_of_band(self.stoch)
		self.nb_strategies += 1

		self.total_vote = self.rsi_vote + self.cci_vote + self.stoch_vote
		self.vote = self.total_vote / self.nb_strategies

		#BUY LOW: When trend is DOWN and STRONG in OVERSOLD position
		if self.trend_dir is self.DOWNTREND and self.trend_str == self.STRONG and self.vote <= self.buythresh:
		#if self.trend_dir is not self.UPTREND and self.trend_str == self.STRONG and self.vote <= self.buythresh:
			self.mylogger.logger.debug("%s [%s] [BUY] OVERSOLD CONDITION MET" % (self.tstamp, self.stock.symbol))
			self.signal = self.BUY

		# SELL: While trend is UP and STRONG in OVERBOUGHT position
		elif self.trend_dir is self.UPTREND and self.trend_str == self.STRONG and self.vote >= self.sellthresh:
		#elif self.trend_dir is not self.DOWNTREND  and self.trend_str == self.STRONG and self.vote >= self.sellthresh:
			self.mylogger.logger.debug("%s [%s] [SELL] OVERBOUGHT CONDITION MET" % (self.tstamp, self.stock.symbol))
			self.signal = self.SELL

		# SELL: TAKE PROFIT
		elif self.stock.change is not None and self.stock.change > 20:
			self.mylogger.logger.debug("%s [%s] [SELL] TAKE PROFIT CONDITION MET" % (self.tstamp, self.stock.symbol))
			self.signal = self.SELL

		# SELL: STOP LOSS
		elif self.stock.change is not None and self.stock.change < -20:
			self.mylogger.logger.debug("%s [%s] [BUY] STOP LOSS CONDITION MET" % (self.tstamp, self.stock.symbol))
			self.signal = self.SELL

		#HOLD: Do nothing rest of the time
		else:
			self.signal = self.NEUTRAL

		self.__print_data()
		self.__print_vote()
		self.__print_signal()

		return self.signal, abs(self.vote)
