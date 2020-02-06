
class MMStrategy():

	def __init__(self):
		self.prev_macdhist = 0
		self.prev_ema = 0
		self.BUY = 1
		self.SELL = -1
		self.HOLD = 0

	def take_profit_stop_loss(self, close, buyprice):
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

	def macd_zero_crossing(self, macdhist):
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

	def rsi_out_of_band(self, rsi):
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

	def boll_out_of_band(self, close, bollbot, bolltop):
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

	def cci_out_of_band(self, cci):
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

	def ema_trend(self, ema):
		if ema is None or self.prev_ema is None:
			direction = 0
		else:

			#trade only when ema 200 is going up.
			ema_trend = ema - self.prev_ema
			if ema_trend > 0:
				direction = 1
			elif ema_trend < 0:
				direction = -1
			else:
				signal = 0

			self.prev_ema = ema

		return direction

	def adx_out_of_band(self, ema, adx):
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

	def run_strategy(self, tstamp, row, stock):
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

		print("\n%s [%8s] close %8.3f, volume %8d, macd %8.3f, macd_signal %8.3f, macdhist %8.3f, rsi %8.3f, cci %8.3f, bolltop %8.3f, bollbot %8.3f, ema %8.3f, adx %8.3f" % (
			self.tstamp, stock.symbol, self.close, self.volume, self.macd, self.macd_signal, self.macdhist, self.rsi, self.cci, self.bolltop, self.bollbot, self.ema, self.adx))

		signal = 0
		self.nb_strategies = 0
		self.ema_direction = 0

		self.profit_loss = 0
		self.macd_vote = 0
		self.rsi_vote = 0
		self.boll_vote = 0
		self.cci_vote = 0
		self.adx_vote = 0
		self.total_vote = 0

		self.profit_loss = self.take_profit_stop_loss(self.close, stock.buyprice)
		#self.nb_strategies += 1

		#self.macd_vote = self.macd_zero_crossing(self.macdhist)
		#self.nb_strategies += 1

		self.rsi_vote = self.rsi_out_of_band(self.rsi)
		self.nb_strategies += 1

		self.boll_vote = self.boll_out_of_band(self.close, self.bollbot, self.bolltop)
		self.nb_strategies += 1

		self.cci_vote = self.cci_out_of_band(self.cci)
		self.nb_strategies += 1

		#self.ema_direction = self.ema_trend(self.ema)
		#self.nb_strategies += 1

		self.ema_direction = self.ema_trend(self.ema)
		self.adx_vote = self.adx_out_of_band(self.ema_direction, self.adx)
		self.nb_strategies += 1

		self.total_vote = self.rsi_vote + self.boll_vote + self.cci_vote + self.adx_vote
		self.vote = self.total_vote / self.nb_strategies

		print("%s [%8s] [%d/%d](%.2f) position %d, ema_direction %3d, take_profit_stop_loss %3d, rsi_out_of_band %3d, boll_out_off_band %3d, cci %3d, adx %3d" % (
				self.tstamp, stock.symbol, self.total_vote, self.nb_strategies, self.vote, stock.position, self.ema_direction, self.profit_loss, self.rsi_vote, self.boll_vote, self.cci_vote, self.adx_vote))

		if self.vote >= self.BUY * 0.5:
			signal = self.BUY
		elif self.vote <= self.SELL * 1 and stock.position == 1:
			signal = self.SELL
		else:
			signal = 0

		return signal
