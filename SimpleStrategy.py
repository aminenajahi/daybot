
class SimpleStrategy():

	def __init__(self):
		self.stopclose = None
		self.prevclose = None

	def trailing_stop(self, close, ratio):
		if close is None or self.stopclose is None or self.prevclose is None:
			signal = 0
			self.stopclose = close
			self.prevclose = close
		else:
			if close < self.stopclose:
				signal = -1
			elif close > self.prevclose:
				self.stopclose = close * ratio
				signal = 0
			else:
				signal = 0
		print("signal %d, close %8.2f, prevclose %8.2f, stopclose %8.2f" % (signal, close, self.prevclose, self.stopclose))
		self.prevclose = close

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

		signal = self.trailing_stop(self.close, 0.85)

		return signal
