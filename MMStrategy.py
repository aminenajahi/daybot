
class MMStrategy():

	def __init__(self):
		self.stock = None
		self.prev_macdhist = 0
		self.prev_ema = 0
		self.BUY = 1
		self.SELL = -1
		self.HOLD = 0

	def __take_profit_stop_loss(self, close, buyprice):
		if buyprice == 0 or close == 0:
			signal = 0
		else :
			if close > buyprice * 1.2:
				signal = self.SELL
			elif close < buyprice * 0.8:
				signal = self.SELL
			else:
				signal = self.HOLD

		return signal

	def __macd_zero_crossing(self, macdhist):
		if macdhist is None:
			signal = 0
		else:
			if self.prev_macdhist < 0 and macdhist >= 0:
				signal = self.BUY
			elif self.prev_macdhist >= 0 and macdhist < 0:
				signal = self.SELL
			else:
				signal = self.HOLD

			self.prev_macdhist = macdhist

		return signal

	def __rsi_out_of_band(self, rsi):
		if rsi is None:
			signal = 0
		else:
			if rsi < 30:
				signal = self.BUY
			elif rsi > 70:
				signal = self.SELL
			else:
				signal = self.HOLD

		return signal

	def __boll_out_of_band(self, close, bollbot, bolltop):
		if close is None or bollbot is None or bolltop is None:
			signal = 0
		else:
			if close < bollbot:
				signal = self.BUY
			elif close > bolltop:
				signal = self.SELL
			else:
				signal = self.HOLD

		return signal

	def __cci_out_of_band(self, cci):
		if cci is None:
			signal = 0
		else:
			if cci < -100:
				signal = self.BUY
			elif cci > 100:
				signal = self.SELL
			else:
				signal = self.HOLD

		return signal

	def __stoch_out_of_band(self, stoch):
		if stoch is None:
			signal = 0
		else:
			if stoch < 20:
				signal = self.BUY
			elif stoch > 80:
				signal = self.SELL
			else:
				signal = self.HOLD

		return signal

	def __ema_trend(self, ema):
		if ema is None or self.prev_ema is None:
			signal = 0
		else:

			#trade only when ema 200 is going up.
			ema_trend = ema - self.prev_ema
			if ema_trend > 0:
				signal = self.BUY
			elif ema_trend < 0:
				signal = self.HOLD
			else:
				signal = 0

			self.prev_ema = ema

		return signal

	def __adx_out_of_band(self, ema, adx):
		if adx is None or ema is None:
			signal = 0
		else:
			if adx > 25 and ema == 1 :
				signal = self.SELL
			elif adx > 25 and ema == -1:
				signal = self.SELL
			else:
				signal = self.HOLD

		return signal

	def __print_data(self):
		print("\n%s [%s] close %8.3f, volume %8d, ema %8.2f macd %8.3f, macd_signal %8.3f, macdhist %8.3f, rsi %8.3f, cci %8.3f, bolltop %8.3f, bollbot %8.3f, adx %8.3f, stoch %8.3f " % (
				self.tstamp, self.stock.symbol, self.close, self.volume, self.ema, self.macd, self.macd_signal,
				self.macdhist, self.rsi, self.cci, self.bolltop, self.bollbot, self.adx, self.stoch))

	def __print_vote(self):
		print("%s [%s] [%d/%d](%.2f) position %d, ema_direction %3d, profit_loss_vote %3d, rsi_out_of_band %3d, boll_out_off_band %3d, cci %3d, adx %3d stoch %3d" % (
				self.tstamp, self.stock.symbol, self.total_vote, self.nb_strategies, self.vote, self.stock.position, self.ema_vote, self.profit_loss_vote, self.rsi_vote, self.boll_vote, self.cci_vote, self.adx_vote, self.stoch_vote))

	def run_strategy(self, tstamp, row, stock):
		self.stock = stock
		self.tstamp = tstamp
		self.close = row['4. close']
		self.volume = row['5. volume']
		self.macdhist = row['trend_macd_diff']
		self.macd = row['trend_macd']
		self.macd_signal = row['trend_macd_signal']
		self.rsi = row['momentum_rsi']
		self.cci = row['trend_cci']
		self.bolltop = row['volatility_bbh']
		self.bollbot = row['volatility_bbl']
		self.adx = row['trend_adx']
		self.ema = row['ema']
		self.stoch = row['momentum_stoch_signal']

		self.__print_data()

		self.signal = 0
		self.nb_strategies = 0
		self.ema_vote = 0
		self.profit_loss_vote = 0
		self.macd_vote = 0
		self.rsi_vote = 0
		self.boll_vote = 0
		self.cci_vote = 0
		self.adx_vote = 0
		self.stoch_vote = 0
		self.total_vote = 0

		#self.profit_loss_vote = self.take_profit_stop_loss(self.close, stock.avgbuyprice)
		#self.nb_strategies += 1

		#self.macd_vote = self.macd_zero_crossing(self.macdhist)
		#self.nb_strategies += 1

		self.rsi_vote = self.__rsi_out_of_band(self.rsi)
		self.nb_strategies += 1

		self.boll_vote = self.__boll_out_of_band(self.close, self.bollbot, self.bolltop)
		self.nb_strategies += 1

		self.cci_vote = self.__cci_out_of_band(self.cci)
		self.nb_strategies += 1

		self.stoch_vote = self.__stoch_out_of_band(self.stoch)
		self.nb_strategies += 1

		#self.ema_vote = self.__ema_trend(self.ema)
		#self.nb_strategies += 1

		self.ema_vote = self.__ema_trend(self.ema)
		self.adx_vote = self.__adx_out_of_band(self.ema_vote, self.adx)
		self.nb_strategies += 1

		self.total_vote = self.rsi_vote + self.boll_vote + self.cci_vote + self.adx_vote + self.stoch_vote
		self.vote = self.total_vote / self.nb_strategies

		self.__print_vote()

		if self.vote > self.BUY * 0.5:
			self.signal = self.BUY
		elif self.vote < self.SELL * 0.75:
			self.signal = self.SELL
		else:
			self.signal = 0

		return self.signal, abs(self.vote)
