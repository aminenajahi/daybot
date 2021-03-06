from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import ta
import time
import pandas as pd
import talib
from datetime import datetime
from ta.trend import SMAIndicator, EMAIndicator

class Market(object):

	keyindex = 0
	apikeys = []

	def __init__(self):
		self.ts = {}
		Market.apikeys = ['LCN3E4TILGN8BPA7']
		#Market.apikeys = ['LCN3E4TILGN8BPA7',
		#				  '2XX277IOADP39LCC',
		#				  'LBLM8TNLD58X9U0T',
		#				  'DRHEONQETBS06FFM',
		#				  'LCPPJ4DYCRDMQP3M',
		#				  'PF37G8RTPAJMGHL0',
		#				  '2LOK334TT6QLRNRP',
		#				  'ULEQCP1IEB74CNGN',
		#				  'UMJN1TU8WPP0RTUT',
		#				  '9CQ582Q4P5G4R7QD']

		for i in range(len(Market.apikeys)):
			self.ts[i] = TimeSeries(key=Market.apikeys[i], output_format='pandas')

		self.period = None
		self.data = None


	def isPostClose(self, timenow):
		weekday = datetime.today().weekday()
		postclosetime = datetime.now().replace(hour=20, minute=00)
		closetime = datetime.now().replace(hour=16, minute=00)

		if weekday < 5 and timenow > closetime and timenow > postclosetime:
			ispostclose = True
		else:
			ispostclose = False

		return ispostclose

	def isPreOpen(self, timenow):
		weekday = datetime.today().weekday()
		preopentime = datetime.now().replace(hour=4, minute=00)
		opentime = datetime.now().replace(hour=9, minute=30)

		if weekday < 5 and timenow < opentime and timenow > preopentime:
			ispreopen = True
		else:
			ispreopen = False

		return ispreopen

	def isOpen(self, timenow):
		weekday = datetime.today().weekday()
		opentime = datetime.now().replace(hour=9, minute=30)
		closetime = datetime.now().replace(hour=16, minute=00)

		if weekday < 5 and timenow > opentime and timenow < closetime:
			isopen = True
		else:
			isopen = False

		return isopen

	def getDailyData(self, symbol, since, debug=False):
		try:
			print("GET DAILY DATA")
			print("using key [%d/%d] = %s "% (Market.keyindex, len(Market.apikeys), Market.apikeys[Market.keyindex]))
			data, meta_data = self.ts[Market.keyindex].get_daily(symbol=symbol, outputsize='full')
			Market.keyindex = (Market.keyindex + 1) % len(Market.apikeys)

			self.data = data
			self.meta_data = meta_data
			self.data = self.data.sort_index()

			# map values to standard OHLC format
			self.data['O'] = self.data['1. open']
			self.data['H'] = self.data['2. high']
			self.data['L'] = self.data['3. low']
			self.data['C'] = self.data['4. close']
			self.data['V'] = self.data['5. volume']

			if debug:
				print("===VALUES===")
				print(self.data)


			# add trend indicator.
			self.data = ta.utils.dropna(self.data)
			self.data['sma20'] = SMAIndicator(close=self.data['C'], n=20, fillna=True).sma_indicator()
			self.data['sma50'] = SMAIndicator(close=self.data['C'], n=50, fillna=True).sma_indicator()
			self.data['sma100'] = SMAIndicator(close=self.data['C'], n=100, fillna=True).sma_indicator()
			self.data['sma200'] = SMAIndicator(close=self.data['C'], n=200, fillna=True).sma_indicator()

			self.data['ema9'] = EMAIndicator(close=self.data['C'], n=9, fillna=True).ema_indicator()
			self.data['ema20'] = EMAIndicator(close=self.data['C'], n=20, fillna=True).ema_indicator()

			self.data = ta.add_all_ta_features(self.data, open="O", high="H", low="L", close="C", volume="V", fillna=True)
			self.data = self.data.loc[self.data.index >= since]

			candle_names = talib.get_function_groups()['Pattern Recognition']
			if debug:
				print(candle_names)

			included_items = ('CDLDOJI',
							  'CDLHAMMER',
							  'CDLEVENINGSTAR',
							  'CDLHANGINGMAN',
							  'CDLSHOOTINGSTAR')
			candle_names = [candle for candle in candle_names if candle in included_items]

			for candle in candle_names:
				self.data[candle] = getattr(talib, candle)(self.data['O'], self.data['H'],
														   self.data['L'], self.data['C'])

			self.data['action'] = 0

			if debug:
				print("===VALUES===")
				print(self.data)

		except:
			print("ERROR GETTING MARKET DATA")
			time.sleep(60)
			self.data = None

		# max 5 api calls per minutes
		#time.sleep(60 / (2 * len(Market.apikeys)))
		#time.sleep(60 / 4)

		return self.data

	def getIntraDayData(self, symbol, since, period, debug=False):
		try:
			print("GET INTRADAY DATA")
			print("using key [%d/%d] = %s "% (Market.keyindex, len(Market.apikeys), Market.apikeys[Market.keyindex]))
			data, meta_data = self.ts[Market.keyindex].get_intraday(symbol=symbol, interval=str(period) + "min", outputsize='full')
			Market.keyindex = (Market.keyindex + 1) % len(Market.apikeys)

			self.data = data
			self.meta_data = meta_data
			self.data = self.data.sort_index()

			# map values to standard OHLC format
			self.data['O'] = self.data['1. open']
			self.data['H'] = self.data['2. high']
			self.data['L'] = self.data['3. low']
			self.data['C'] = self.data['4. close']
			self.data['V'] = self.data['5. volume']

			if debug:
				print("===VALUES===")
				print(self.data)

			print("===CALCULATE ALL TA===")
			self.data = ta.utils.dropna(self.data)
			self.data['sma20'] = SMAIndicator(close=self.data['C'], n=20, fillna=True).sma_indicator()
			self.data['sma50'] = SMAIndicator(close=self.data['C'], n=50, fillna=True).sma_indicator()
			self.data['sma100'] = SMAIndicator(close=self.data['C'], n=100, fillna=True).sma_indicator()
			self.data['sma200'] = SMAIndicator(close=self.data['C'], n=200, fillna=True).sma_indicator()

			self.data['ema9'] = EMAIndicator(close=self.data['C'], n=9, fillna=True).ema_indicator()
			self.data['ema20'] = EMAIndicator(close=self.data['C'], n=20, fillna=True).ema_indicator()

			self.data = ta.add_all_ta_features(self.data, open="O", high="H", low="L", close="C", volume="V", fillna=True)
			self.data = self.data.loc[self.data.index >= since]

			candle_names = talib.get_function_groups()['Pattern Recognition']
			if debug:
				print(candle_names)

			included_items = ('CDLDOJI',
							 'CDLEVENINGSTAR',
							 'CDLHAMMER',
							 'CDLHANGINGMAN',
							 'CDLSHOOTINGSTAR')
			candle_names = [candle for candle in candle_names if candle in included_items]

			for candle in candle_names:
				self.data[candle] = getattr(talib, candle)(self.data['O'], self.data['H'], self.data['L'], self.data['C'])

			self.data['action'] = 0
			
			if debug:
				print("===VALUES===")
				print(self.data)

		except:
			print("ERROR GETTING MARKET DATA")
			time.sleep(60)
			self.data = None

		# max N api calls per minutes
		#time.sleep(60 / (2 * len(Market.apikeys)))
		#time.sleep(60 / 4)

		return self.data

