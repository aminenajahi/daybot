import ta
import time
import pandas as pd
import talib
from datetime import datetime
from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order
import random as random
import uuid
import ezibpy
import os
from ta.trend import SMAIndicator, EMAIndicator

class IBMarket(object):
	conn = ezibpy.ezIBpy()
	conn.connect(clientId=101, host="localhost", port=4001)
	market_data_available = {}
   
	# define custom callback
	def ibCallback(self, caller, msg, **kwargs):
		#print(caller)
		#print(msg)
		try:
			if caller == "handleHistoricalData":
				completed = kwargs.get('completed')
				if completed == True:
					symbol = IBMarket.conn.contracts[msg.reqId].m_symbol
					print("Historical data downloaded for %s" % symbol)                    
					IBMarket.market_data_available[symbol] = True
		except:
			print("ERROR HANDLE CALLBACK")

	def __init__(self, rth=False):
		self.period = None
		self.data = None
		self.rth = rth       

		IBMarket.conn.ibCallback = self.ibCallback

	def isPostClose(self, timenow):
		weekday = datetime.today().weekday()
		postclosetime = datetime.now().replace(hour=20, minute=00)
		closetime = datetime.now().replace(hour=16, minute=00)

		if weekday < 5 and timenow > closetime and timenow < postclosetime:
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
		#try:
		print("GET IBKR INTRADAY DATA")
		now = datetime.now()
		
		print("CREATE CONTRACT FOR %s" % symbol)
		contract = IBMarket.conn.createStockContract(symbol)

		dirname = os.path.dirname(__file__)
		filename = "data/daily/"+symbol+"_"+now.strftime("%Y_%m_%d")+"_1_day.csv"
		
		if os.path.isfile(filename) == True:
			os.remove(filename)

		print("REQUEST HISTORICAL DATA FOR %s SINCE %s" % (symbol, since))
		IBMarket.market_data_available[symbol] = False
		IBMarket.conn.requestHistoricalData(contract, rth=self.rth, resolution="1 day", lookback="12 M", csv_path='data/daily/')
		
		print("WAIT FOR DATA...")
		while IBMarket.market_data_available[symbol] == False:
			time.sleep(5)
		IBMarket.market_data_available[symbol] = False

		print("RENAME CSV FILE TO %s" % filename)
		os.rename("data/daily/"+symbol+".csv", filename)
		
		print("READ CSV FILE:%s" % filename)
		self.data = pd.read_csv(filename, index_col='datetime', parse_dates=True)
		self.data = self.data.sort_index()
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
		
		self.data = ta.add_all_ta_features(self.data, open="O", high="H", low="L", close="C",
										volume="V", fillna=True)

		self.data = self.data.loc[self.data.index >= since]

		print("===CALCULATE DOJI===")        
		candle_names = talib.get_function_groups()['Pattern Recognition']
		included_items = ('CDLDOJI',
							'CDLHAMMER',
							'CDLEVENINGSTAR',
							'CDLHANGINGMAN',
							'CDLSHOOTINGSTAR')
		candle_names = [candle for candle in candle_names if candle in included_items]

		for candle in candle_names:
			self.data[candle] = getattr(talib, candle)(self.data['O'], self.data['H'],
													self.data['L'], self.data['C'])

		if debug:
			print("===VALUES===")
			print(self.data[['C','V', 'WAP', 'sma20','sma50','sma100','sma200','momentum_rsi', 'trend_cci', 'momentum_stoch_signal', 'trend_adx']])

		#except:
		#	print("ERROR GETTING MARKET DATA")
		#	time.sleep(60)
		#	self.data = None

		#30 request / 10 mins -> need to wait 20 secs
		time.sleep(20)
		return self.data

	def getIntraDayData(self, symbol, since, period, live=False, debug=False):
		#try:
		print("GET IBKR INTRADAY DATA")
		if live == True:
			lookback = int(period * 1600 / 60 / 24)
		else:
			dtime = datetime.now() - datetime.strptime(since, '%Y-%m-%d')
			#lookback = dtime.total_seconds() / 60 / 60 / 24
			lookback = 7
			

		now = datetime.now()
	
		print("CREATE CONTRACT FOR %s" % symbol)
		contract = IBMarket.conn.createStockContract(symbol)

		dirname = os.path.dirname(__file__)
		filename = "data/intraday/"+symbol+"_"+now.strftime("%Y_%m_%d")+"_"+str(period)+"_min.csv"
		
		if os.path.isfile(filename) == True:
			os.remove(filename)

		print("REQUEST HISTORICAL DATA FOR %s, LOOKBACK %d DAYS, SINCE %s, RTH:%d" % (symbol, lookback, since, self.rth))
		IBMarket.market_data_available[symbol] = False
		IBMarket.conn.requestHistoricalData(contract, rth=self.rth, resolution=str(period) + " mins", lookback=str(lookback) + " D", csv_path='data/intraday/')
	
		print("WAIT FOR DATA...")
		while IBMarket.market_data_available[symbol] == False:
			time.sleep(5)
		IBMarket.market_data_available[symbol] = False

		print("RENAME CSV FILE")
		os.rename("data/intraday/"+symbol+".csv", filename)
		
		print("READ CSV DATA")
		self.data = pd.read_csv(filename, index_col='datetime', parse_dates=True)
		self.data = self.data.sort_index()
		self.data = self.data[:-1]
		if debug:
			print("===VALUES===")
			print(self.data)

		print("===CALCULATE SMA===")
		# add trend indicator.
		#self.data['sma20'] = self.data['C'].rolling(20, min_periods=20).mean()
		#self.data['sma50'] = self.data['C'].rolling(50, min_periods=50).mean()
		#self.data['sma100'] = self.data['C'].rolling(100, min_periods=100).mean()
		#self.data['sma200'] = self.data['C'].rolling(200, min_periods=200).mean()
	   
		print("===CALCULATE ALL TA===")
		self.data = ta.utils.dropna(self.data)
		self.data['sma20'] = SMAIndicator(close=self.data['C'], n=20, fillna=True).sma_indicator()
		self.data['sma50'] = SMAIndicator(close=self.data['C'], n=50, fillna=True).sma_indicator()
		self.data['sma100'] = SMAIndicator(close=self.data['C'], n=100, fillna=True).sma_indicator()
		self.data['sma200'] = SMAIndicator(close=self.data['C'], n=200, fillna=True).sma_indicator()
		
		self.data['ema9'] = EMAIndicator(close=self.data['C'], n=9, fillna=True).ema_indicator()
		self.data['ema20'] = EMAIndicator(close=self.data['C'], n=20, fillna=True).ema_indicator()
		
		self.data = ta.add_all_ta_features(self.data, open="O", high="H", low="L", close="C",
										volume="V", fillna=True)

		self.data['mvwap'] = self.data['volume_vwap'].rolling(14, min_periods=14).mean()
		self.data = self.data.loc[self.data.index >= since]

		print("===CALCULATE DOJI===")        
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

		if debug:
			print("===VALUES===")
			print(self.data)

		#except:
		#    print("ERROR GETTING MARKET DATA")
		#    time.sleep(60)
		#    self.data = None

		return self.data

