import math
import talib
from datetime import datetime

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

		self.LONG = -1
		self.SHORT = 1

		self.buythresh = self.BUY * 0.5
		self.sellthresh = self.SELL * 0.5

		self.trend_strenght_str = {self.WEAK: "WEAK", self.STRONG: "STRONG"}
		self.trend_dir_str = {self.DOWNTREND: "DOWNTREND", self.NEUTRAL: "NEUTRAL", self.UPTREND: "UPTREND"}
		self.rsi_str = {self.OVERSOLD: "OVERSOLD", self.OVERBOUGHT: "OVERBOUGHT"}
		self.signal_str = {self.BUY: "BUY", self.SELL: "SELL", self.NEUTRAL: "NEUTRAL"}

		self.prevclose = 0
		self.zone = self.NEUTRAL
		self.stop_buyprice = 0
		self.stop_sellprice = 0
		self.mean = 0
		self.prevmean = 0
		self.stoplimit = 0
		

		#self.ta = pd.DataFrame(columns=['TS', 'SIGNAL', 'SYMBOL', 'C', 'SHARES', 'AVG COST', 'CHANGE', 'ADX', 'SMA20', 'SMA50', 'SMA100', 'SMA200', 'RSI', 'CCI', 'STOCH', 'CMF'])
		#self.vote = pd.DataFrame(columns=['TS', 'SIGNAL', 'SYMBOL', 'TREND_DIR', 'TREND_STR', 'RSI_VOTE', 'CCI_VOTE', 'STOCH_VOTE', 'CMF_VOTE', 'AGGR_VOTE'])

	def __trend_direction(self, close, sma20, sma50, sma100, sma200):
		if close is None or sma20 is None or sma50 is None:
			signal = self.NEUTRAL
		elif close >= sma20 and close >= sma50 and close >= sma100 and sma20 > sma50 * 1.0025 and sma50 > sma100:
			signal = self.UPTREND
		elif close < sma20 and close < sma50 and close < sma100 and sma20  < sma50 * 0.9975 and sma50 < sma100:
			signal = self.DOWNTREND
		else:
			signal = self.NEUTRAL

		return signal

	def __short_trend_direction(self, close, ema9, sma20):
		if close is None or ema9 is None or sma20 is None:
			signal = self.NEUTRAL
		elif close >= ema9 and close >= sma20 and ema9 > sma20 * 1.0025:
			signal = self.UPTREND
		elif close < ema9 and close < sma20 and ema9 < sma20 * 0.9975:
			signal = self.DOWNTREND
		else:
			signal = self.NEUTRAL

		return signal

	def __trend_strength(self, adx):
		if adx is None:
			signal = self.NEUTRAL
		else:
			if adx < 25 and adx > 10:
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

	def __crossing_vwap(self, mean, prevmean, vwap):
		if mean == 0  or prevmean == 0 or  vwap == 0:
			signal = self.NEUTRAL
			print("VWAP INVALID VALUES")
		elif mean > vwap and prevmean <= vwap:
			signal = self.BUY
			print("VWAP BUY SIGNAL")
		elif mean < vwap and prevmean >= vwap:
			signal = self.SELL
			print("VWAP SELL SIGNAL")
		else:
			signal = self.NEUTRAL
			print("VWAP NO SIGNAL")

		return signal
	
	def __print_data(self):
		self.mylogger.logger.debug("%s [%s] positions %d, avg_price %8.3f, close %8.3f, prevclose %8.3f, change %8.2f%%, volume %8d, vwap %8.3f" % (
				self.tstamp, self.stock.symbol, self.stock.totalbuysize, self.avgprice, self.close, self.prevclose, self.stock.change, self.volume, self.vwap))
		self.mylogger.logger.debug("%s [%s] adx %8.3f, atr %8.3f, sma20 %8.3f, sma50 %8.3f, sma100 %8.3f sma200 %8.3f" % (
				self.tstamp, self.stock.symbol, self.adx, self.atr, self.sma20, self.sma50, self.sma100, self.sma200))
		self.mylogger.logger.debug("%s [%s] ema9 %8.3f, ema20 %8.3f" % (
				self.tstamp, self.stock.symbol, self.ema9, self.ema20))
		self.mylogger.logger.debug("%s [%s] rsi %8.3f, cci %8.3f, stoch %8.3f" % (
				self.tstamp, self.stock.symbol, self.rsi, self.cci, self.stoch))
		self.mylogger.logger.debug("%s [%s] doji %d,  hammer: %d, eveningstar %d, handingmand %d, shootingstar %d " % (
				self.tstamp, self.stock.symbol, self.doji, self.hammer, self.eveningstar, self.hangingman, self.shootingstar))
		self.mylogger.logger.debug("%s [%s] sma trend_dir %d, ema trend_dir %d, trend_str %d" % (
				self.tstamp, self.stock.symbol, self.trend_dir, self.short_trend_dir, self.trend_str))

	def __print_vote(self):
		self.mylogger.logger.debug("%s [%s] vote %.2f, rsi_vote %d, cci_vote %d, stoch_vote %d, vwap_vote %d" % (
				self.tstamp, self.stock.symbol, self.vote, self.rsi_vote, self.cci_vote, self.stoch_vote, self.vwap_vote))

	def __check_stop_loss_take_profit(self):
	# SELL: MAXIMUM TAKE PROFIT
		if self.stock.totalbuysize > 0 and self.stock.change > 20:
			self.mylogger.logger.debug("%s [%s] [SELL] TAKE PROFIT CONDITION MET" % (self.tstamp, self.stock.symbol))
			signal = self.SELL
			riskfactor = 1
		
		# SELL: MAXIMUM STOP LOSS
		elif self.stock.totalbuysize > 0 and self.stock.change < -6:
			self.mylogger.logger.debug("%s [%s] [SELL] STOP LOSS CONDITION MET" % (self.tstamp, self.stock.symbol))
			signal = self.SELL
			riskfactor = 1
		else:
			signal = self.NEUTRAL
			riskfactor = 0

		return signal, riskfactor

	def __run_trend_algo(self):
		signal = self.NEUTRAL
		position = 0
	
		#=== STEP ONE, CHECK EXISTING POSITIONS ===
		if self.stock.long == 1:
			#Update limit order after restart

			#SELL LONG ON DOWNSTREND
			if self.short_trend_dir == self.DOWNTREND and self.stock.totalbuysize > 0:
				signal = self.SELL
				riskfactor = 1
				position = self.LONG
				self.mylogger.logger.debug("%s [%s] [SELL] MM LONG DOWNTREND TRIGGER" % (self.tstamp, self.stock.symbol))
				return signal, riskfactor, position
			
		if self.stock.long == 0:
			#BUY LONG ON UPTREND
			if self.short_trend_dir == self.UPTREND and self.stock.totalbuysize == 0:
				signal = self.BUY
				riskfactor = 1
				position = self.LONG
				self.mylogger.logger.debug("%s [%s] [BUY] MM LONG UPTREND TRIGGER" % (self.tstamp, self.stock.symbol))
				return signal, riskfactor, position
	
		if self.stock.short == 1:
			#Update limit order after restart
			
			#SELL SHORT ON DOWNSTREND
			if self.short_trend_dir == self.UPTREND and self.stock.totalbuysize > 0:
				signal = self.SELL
				riskfactor = 1
				position = self.SHORT
				self.mylogger.logger.debug("%s [%s] [SELL] MM SHORT DOWNTREND TRIGGER" % (self.tstamp, self.stock.symbol))
				return signal, riskfactor, position
			
		if self.stock.short == 0:
			#BUY SHORT ON DOWNTREND
			if self.short_trend_dir == self.DOWNTREND and self.stock.totalbuysize == 0:
				signal = self.BUY
				riskfactor = 1
				position = self.SHORT
				self.mylogger.logger.debug("%s [%s] [BUY] MM SHORT DOWNTREND TRIGGER" % (self.tstamp, self.stock.symbol))
				return signal, riskfactor, position
	
		self.mylogger.logger.debug("%s [%s] [NEUTRAL] MM ALGO NO TRIGGER" % (self.tstamp, self.stock.symbol))
		riskfactor = 1
		signal = self.NEUTRAL			
		return signal, riskfactor, position

	""" def __run_mm_algo(self):
		signal = self.NEUTRAL
		position = 0
	
		#=== STEP ONE, CHECK EXISTING POSITIONS ===
		if self.stock.long == 1:
			#Update limit order after restart
			self.stoplimit = self.stock.buyprice * 0.97
	
			#RSI SELL LONG ON STRONG UPTREND
			if self.close > self.avgprice and self.vote > self.sellthresh and self.trend_dir == self.UPTREND and self.trend_dir_str == self.STRONG and self.stock.totalbuysize > 0:
				signal = self.SELL
				riskfactor = 1
				position = self.LONG
				self.mylogger.logger.debug("%s [%s] [SELL] MM LONG RSI TRIGGER" % (self.tstamp, self.stock.symbol))
				return signal, riskfactor, position
	
			#RISK REWARD RATION MET, SELL LONG
			if self.stock.change >= 10 and self.stock.totalbuysize > 0:
				signal = self.SELL
				riskfactor = 1
				position = self.LONG
				self.mylogger.logger.debug("%s [%s] [SELL] MM LONG 3/10%% R/R TRIGGER" % (self.tstamp, self.stock.symbol))
				return signal, riskfactor, position
			
			#STOP LIMIT CHECK FOR LONG POSITIONS
			if self.close < self.stoplimit and self.stock.totalbuysize > 0:
				signal = self.SELL
				riskfactor = 1
				self.stoplimit = 0
				position = self.LONG
				self.mylogger.logger.debug("%s [%s] [SELL] MM LONG STOP LIMIT TRIGGER" % (self.tstamp, self.stock.symbol))
				return signal, riskfactor, position

		if self.stock.long == 0:
			#RSI BUY LONG ON STRONG DOWNTREND
			if self.vote < self.buythresh and self.trend_dir == self.DOWNTREND and self.trend_dir_str == self.STRONG and self.stock.totalbuysize == 0:
				signal = self.BUY
				riskfactor = 1
				position = self.LONG
				self.mylogger.logger.debug("%s [%s] [BUY] MM LONG RSI TRIGGER" % (self.tstamp, self.stock.symbol))
				return signal, riskfactor, position
	
		
		self.mylogger.logger.debug("%s [%s] [NEUTRAL] MM ALGO NO TRIGGER" % (self.tstamp, self.stock.symbol))
		riskfactor = 1
		signal = self.NEUTRAL			
		return signal, riskfactor, position """

	""" def __run_mm_algo(self):
		signal = self.NEUTRAL
		position = 0
	
		self.mylogger.logger.debug("%s [%s] IN ZONE %s" % (self.tstamp, self.stock.symbol, self.signal_str[self.zone]))

		# ZONE checking
		if self.signal != self.SELL:
			#BUY LOW: When trend is DOWN and STRONG in OVERSOLD position
			if self.trend_dir is self.DOWNTREND and (self.trend_str == self.WEAK or self.trend_str == self.STRONG) and self.vote < self.buythresh:
			#if self.trend_dir is not self.UPTREND and self.trend_str == self.STRONG and self.vote <= self.buythresh:			
				#self.signal = self.BUY
				self.zone = self.BUY
				self.mylogger.logger.debug("%s [%s] [BUY] OVERSOLD CONDITION MET, ENTERING %s ZONE" % (self.tstamp, self.stock.symbol, self.signal_str[self.zone]))
				if self.close < self.prevclose:
					self.stop_buyprice = self.close + 2 * self.atr
					self.mylogger.logger.debug("%s [%s] [BUY] ADJUSTING STOP BUY PRICE @ %.2f" % (self.tstamp, self.stock.symbol, self.stop_buyprice))
			
			# SELL: While trend is UP and STRONG in OVERBOUGHT position
			elif self.trend_dir is self.UPTREND and (self.trend_str == self.WEAK or self.trend_str == self.STRONG)  and self.vote > self.sellthresh and self.stock.totalbuysize > 0:
			#elif self.trend_dir is not self.DOWNTREND  and self.trend_str == self.STRONG and self.vote >= self.sellthresh:
				#self.signal = self.SELL
				self.zone = self.SELL
				self.mylogger.logger.debug("%s [%s] [SELL] OVERBOUGHT CONDITION MET, ENTERING %s ZONE" % (self.tstamp, self.stock.symbol, self.signal_str[self.zone]))
				if self.close > self.prevclose:
					self.stop_sellprice = self.close - 2 * self.atr
					self.mylogger.logger.debug("%s [%s] [SELL] ADJUSTING STOP SELL PRICE @ %.2f" % (self.tstamp, self.stock.symbol, self.stop_sellprice))

			# BUY when up trend after oversold
			if self.stop_buyprice != 0 and self.close > self.stop_buyprice:
				self.mylogger.logger.debug("%s [%s] [BUY] STOP PRICE CONDITION MET @ %.2f" % (self.tstamp, self.stock.symbol, self.stop_buyprice))
				self.zone = self.NEUTRAL
				self.signal = self.BUY
				self.stop_buyprice = 0
				self.riskfactor = 0.5
			
			# SEll when downtrend after overbought
			elif self.stop_sellprice != 0 and self.close < self.stop_sellprice and self.close > self.avgprice:
				self.mylogger.logger.debug("%s [%s] [SELL] STOP PRICE CONDITION MET @ %.2f" % (self.tstamp, self.stock.symbol, self.stop_sellprice))
				self.zone = self.NEUTRAL
				self.signal = self.SELL
				self.stop_sellprice
				self.riskfactor = 1 """


	def run_strategy(self, tstamp, row, stock):
		self.stock = stock
		self.tstamp = tstamp
		self.high = row['H']
		self.low = row['L']
		self.close = row['C']
		self.volume = row['V']
		self.rsi = row['momentum_rsi']
		self.cci = row['trend_cci']
		self.stoch = row['momentum_stoch_signal']		
		self.ema9 = row['ema9']
		self.ema20 = row['ema20']
		self.sma20 = row['sma20']
		self.sma50 = row['sma50']
		self.sma100 = row['sma100']
		self.sma200 = row['sma200']
		self.adx = row['trend_adx']
		self.atr = row['volatility_atr']
		if self.atr == 0:
			self.atr = self.close * 0.03
	
		self.doji = row['CDLDOJI']
		self.hammer = row['CDLHAMMER']
		self.eveningstar = row['CDLEVENINGSTAR']
		self.hangingman = row['CDLHANGINGMAN']
		self.shootingstar = row['CDLSHOOTINGSTAR']
		self.sum_pv = 0
		self.sum_v = 0
		self.vwap = row['volume_vwap']
		#.mvwap = row['mvwap']
		self.avgprice = self.stock.avgbuyprice
		self.nb_strategies = 0
		self.rsi_vote = 0
		self.cci_vote = 0
		self.stoch_vote = 0
		self.vwap_vote = 0
		self.total_vote = 0
		self.riskfactor = 0
		self.position = 0
		self.signal = self.NEUTRAL
		
		if self.prevclose == 0:
			self.prevclose = self.close

		self.mean = (self.high + self.low + self.close) / 3
		self.trend_dir = self.__trend_direction(self.close, self.sma20, self.sma50, self.sma100, self.sma200)
		self.short_trend_dir = self.__short_trend_direction(self.close, self.ema9, self.sma20)
		self.trend_str = self.__trend_strength(self.adx)
		
		self.rsi_vote = self.__rsi_out_of_band(self.rsi)		
		self.cci_vote = self.__cci_out_of_band(self.cci)
		self.stoch_vote = self.__stoch_out_of_band(self.stoch)

		self.nb_strategies = 3
		self.total_vote = self.rsi_vote + self.cci_vote + self.stoch_vote
		self.vote = self.total_vote / self.nb_strategies

		self.signal, self.riskfactor = self.__check_stop_loss_take_profit()
		self.signal, self.riskfactor, self.position = self.__run_trend_algo()
		#self.signal, self.riskfactor, self.position = self.__run_mm_algo()
		#self.signal, self.riskfactor, self.position = self.__run_vwap_algo()

		self.__print_data()
		self.__print_vote()
		
		self.prevclose = self.close
		self.prevmean = self.mean

		self.mylogger.logger.debug("%s [%s] signal: %d, vote %d, riskfactor %d, position %d" % (self.tstamp, self.stock.symbol, self.signal, abs(self.vote), self.riskfactor, self.position))		
		return self.signal, abs(self.vote), self.riskfactor, self.position
