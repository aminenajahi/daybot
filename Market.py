from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import ta
import time
import pandas as pd
import datetime as datetime

class Market(object):

	def __init__(self, key):
		self.ts = TimeSeries(key=key, output_format='pandas')
		self.period = None
		self.data = None


	def getDailyData(self, symbol, since, debug=False):
		self.data, self.meta_data = self.ts.get_daily(symbol=symbol, outputsize='full')

		self.data = self.data.sort_index()
		if debug:
			print(self.data.head(3))
			print(self.data.tail(3))

		self.data = ta.utils.dropna(self.data)
		self.data = ta.add_all_ta_features(self.data, open="1. open", high="2. high", low="3. low", close="4. close", volume="5. volume", fillna=True)

		#add trend indicator.
		emaindicator = ta.trend.EMAIndicator(close=self.data["4. close"], n=300, fillna = True)
		self.data['ema'] = emaindicator.ema_indicator()
		if debug:
			print(self.data.head(3))
			print(self.data.tail(3))

		self.data = self.data.loc[self.data.index >= since]

		# max 5 api calls per minutes
		time.sleep(15)

		return self.data

	def getIntraDayData(self, symbol, period, debug=False):
		self.data, self.meta_data = self.ts.get_intraday(symbol=symbol, interval=str(period) + "min", outputsize='full')

		self.data = self.data.sort_index()
		if debug:
			print(self.data.head(3))
			print(self.data.tail(3))

		self.data = ta.utils.dropna(self.data)
		self.data = ta.add_all_ta_features(self.data, open="1. open", high="2. high", low="3. low", close="4. close", volume="5. volume", fillna=True)

		#add trend indicator.
		emaindicator = ta.trend.EMAIndicator(close=self.data["4. close"], n=300, fillna = True)
		self.data['ema'] = emaindicator.ema_indicator()
		if debug:
			print(self.data.head(3))
			print(self.data.tail(3))

		# max 5 api calls per minutes
		time.sleep(15)

		return self.data

