from finviz.screener import Screener

class FinvizScreener(object):

	def __init__(self, nb_stocks=10, logger=None):
		print("Create Finviz Screener")
		self.nb_stocks = nb_stocks
		self.logger = logger

	def log(self, str):
		if self.logger is not None:
			self.logger.debug(str)
		else:
			print(str)
		
	def getDailyAlpha(self):
		watchlist = []
		full_list = {}
	
		self.log("=== TOP %d BIGGEST MARKET CAP ===" % self.nb_stocks)
		stock_list = self.top_N_biggest(self.nb_stocks)        
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		self.log("=== TOP %d GAINER ===" % self.nb_stocks)
		stock_list = self.top_N_gainer(self.nb_stocks)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		self.log("=== TOP %d HIGH VOLUME ===" % self.nb_stocks)
		stock_list = self.top_N_high_volume(self.nb_stocks)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		self.log("=== TOP %d HIGH VOLATILE ===" % self.nb_stocks)
		stock_list = self.top_N_volatility(self.nb_stocks)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])
		
		self.log("=== TOP %d OVERSOLD ===" % self.nb_stocks)
		stock_list = self.top_N_oversold(self.nb_stocks)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		self.log("=== TOP %d WEEKLY PERFORMER ===" % self.nb_stocks)
		stock_list = self.top_N_1wperformer(self.nb_stocks)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		self.log("=== TOP %d MONTHLY PERFORMER ===" % self.nb_stocks)
		stock_list = self.top_N_1mperformer(self.nb_stocks)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		watchlist = list(dict.fromkeys(watchlist))
		self.log("=== AGGREGATED TICKERS (%d)====" % len(watchlist))
		self.log(watchlist)

		return watchlist

	def getDailyOversold(self):
		ticker_pool = []
		watchlist = []
		N = 500

		Screener = ()
		self.log("=== TOP %d BIGGEST MARKET CAP ===" % N)
		stock_list = self.top_N_biggest(N)
		for stock in stock_list:
			ticker_pool.append(stock['Ticker'])

		print(ticker_pool)

		self.log("=== TOP %d OVERSOLD ===" % self.nb_stocks)
		#stock_list = self.top_N_oversold(self.nb_stocks, table="Technical", stock_list=ticker_pool)
		stock_list = self.top_N_oversold(self.nb_stocks, stock_list=ticker_pool)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		watchlist = list(dict.fromkeys(watchlist))
		self.log("screener watchlist")
		self.log(watchlist)

		return watchlist

	def getCrossingSMA(self):
		watchlist = []
		N = 100

		self.log("=== TOP %d SMA20 CROSSING SMA50 ===" % N)
		stock_list = self.Top_N_SMA20_crossing_SMA50(N, table='Technical')
		for stock in stock_list:
			ticker = stock['Ticker']
			pct = float(stock['SMA20'].strip('%')) 
			if pct >= -10 and pct <= 10:
				print("[%s]SMA20:%.2f%%" % (ticker, pct))
				watchlist.append(ticker)

		watchlist = list(dict.fromkeys(watchlist))
		self.log("screener watchlist")
		self.log(watchlist)

		return watchlist

	def getDailyAlphaFromBigCaps(self):
		ticker_pool = []
		watchlist = []
		N = 500

		self.log("=== TOP %d BIGGEST MARKET CAP ===" % N)
		stock_list = self.top_N_biggest(N)
		for stock in stock_list:
			ticker_pool.append(stock['Ticker'])

		self.log("=== TOP %d GAINER ===" % self.nb_stocks)
		stock_list = self.top_N_gainer(self.nb_stocks, stock_list=ticker_pool)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		self.log("=== TOP %d HIGH VOLUME ===" % self.nb_stocks)
		stock_list = self.top_N_high_volume(self.nb_stocks, stock_list=ticker_pool)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		self.log("=== TOP %d HIGH VOLATILE ===" % self.nb_stocks)
		stock_list = self.top_N_volatility(self.nb_stocks, stock_list=ticker_pool)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])
		
		self.log("=== TOP %d WEEKLY PERFORMER ===" % self.nb_stocks)
		stock_list = self.top_N_1wperformer(self.nb_stocks, stock_list=ticker_pool)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		self.log("=== TOP %d MONTHLY PERFORMER ===" % self.nb_stocks)
		stock_list = self.top_N_1mperformer(self.nb_stocks, stock_list=ticker_pool)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		watchlist = list(dict.fromkeys(watchlist))
		self.log("screener watchlist")
		self.log(watchlist)

		return watchlist

	def top_N_biggest(self, N, table=None, stock_list=None):
		filters = ['geo_usa', 'sh_curvol_o2000']
		if stock_list is None:
			stock_list = Screener(filters=filters, order='-marketcap', rows=N, table=table)
		else:
			stock_list = Screener(tickers=stock_list, order='-marketcap', rows=N, table=table)
		self.log(stock_list)
		return stock_list

	def Top_N_SMA20_crossing_SMA50(self, N, table=None, stock_list=None):
		filters = ['geo_usa', 'cap_midover', 'sh_avgvol_o2000', 'ta_sma20_cross50']
		if stock_list is None:
			stock_list = Screener(filters=filters, order='sma20', rows=N, table=table)
		else:
			stock_list = Screener(tickers=stock_list, order='sma20', rows=N, table=table)
		self.log(stock_list)
		return stock_list

	def top_N_1wperformer(self, N, table=None, stock_list=None):
		filters = ['geo_usa', 'cap_largeover', 'sh_avgvol_o1000']
		if stock_list is None:
			stock_list = Screener(filters=filters, order='-perf1w', rows=N, table=table)
		else:
			stock_list = Screener(tickers=stock_list, order='-perf1w', rows=N, table=table)
		self.log(stock_list)
		return stock_list

	def top_N_oversold(self, N, table=None, stock_list=None):
		filters = ['geo_usa', 'cap_largeover', 'sh_curvol_o2000']
		if stock_list is None:
			stock_list = Screener(filters=filters, order='rsi', rows=N, table=table)
		else:
			print("from ticker pool")
			#stock_list = Screener(tickers=stock_list, filters=['sh_curvol_o2000'], order='rsi', rows=N, table=table)
			stock_list = Screener(tickers=stock_list, filters=['sh_curvol_o2000'], order='-rsi', rows=N, table=table)
		self.log(stock_list)
		return stock_list

	def top_N_1mperformer(self, N, table=None, stock_list=None):
		filters = ['geo_usa', 'cap_largeover', 'sh_avgvol_o1000']
		if stock_list is None:
			stock_list = Screener(filters=filters, order='-perf4w', rows=N, table=table)
		else:
			stock_list = Screener(tickers=stock_list, order='-perf4w', rows=N, table=table)
		self.log(stock_list)
		return stock_list

	def top_N_gainer(self, N, table=None, stock_list=None):
		filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000']
		if stock_list is None:
			stock_list = Screener(filters=filters, order='-change', rows=N, table=table)
		else:
			stock_list = Screener(tickers=stock_list, order='-change', rows=N, table=table)
		self.log(stock_list)
		return stock_list

	def top_N_looser(self, N, table=None, stock_list=None):
		filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000']
		if stock_list is None:
			stock_list = Screener(filters=filters, order='change', rows=N, table=table)
		else:
			stock_list = Screener(tickers=stock_list, order='change', rows=N, table=table)
		self.log(stock_list)
		return stock_list

	def top_N_high_volume(self, N, table=None, stock_list=None):
		filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000']
		if stock_list is None:
			stock_list = Screener(filters=filters, order='-Volume', rows=N, table=table)
		else:
			stock_list = Screener(tickers=stock_list, order='-Volume', rows=N, table=table)
		self.log(stock_list)
		return stock_list

	def top_N_bouce_back(self, N, table=None, stock_list=None):
		filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000', 'ta_highlow52w_b30h']
		if stock_list is None:
			stock_list = Screener(filters=filters, order='change', rows=N, table=table)
		else:
			stock_list = Screener(tickers=stock_list, order='change', rows=N, table=table)
		self.log(stock_list)
		return stock_list

	def top_N_tanking(self, N, table=None, stock_list=None):
		filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000', 'ta_highlow50d_b30h', 'ta_highlow52w_b30h']
		if stock_list is None:
			stock_list = Screener(filters=filters, order='change', rows=N, table=table)
		else:
			stock_list = Screener(tickers=stock_list, order='change', rows=N, table=table)
		self.log(stock_list)
		return stock_list

	def top_N_volatility(self, N, table=None, stock_list=None):
		filters = ['geo_usa', 'cap_largeover',  'sh_avgvol_o1000']
		if stock_list is None:
			stock_list = Screener(filters=filters, order='-volatility1w', rows=N, table=table)
		else:
			stock_list = Screener(tickers=stock_list, order='-volatility1w', rows=N, table=table)
		self.log(stock_list)
		return stock_list