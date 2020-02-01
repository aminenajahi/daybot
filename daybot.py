# Import the library
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from datetime import datetime
import pandas as pd
import sys
import time
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import ta
import numpy
import logging
import threading
import argparse
import smtplib

lock = threading.Lock()

class Strategies():

	def __init__(self):
		self.prev_macdhist = 0

	def take_profit_stop_loss(self, close, buyprice):
		if buyprice is None or close is None:
			signal = 0
		else :
			if close > buyprice * 1.2:
				signal = 1
			elif close < buyprice * 0.8:
				signal = -1
			else:
				signal = 0

		return signal

	def macd_zero_crossing(self, macdhist):
		if macdhist is None:
			signal = 0
		else:
			if self.prev_macdhist < 0 and macdhist >= 0:
				signal = 1
			elif self.prev_macdhist >= 0 and macdhist < 0:
				signal = -1
			else:
				signal = 0

			self.prev_macdhist = macdhist

		return signal

	def rsi_out_of_band(self, rsi):
		if rsi is None:
			signal = 0
		else:
			if rsi < 30:
				signal = 1
			elif rsi > 70:
				signal = -1
			else:
				signal = 0

		return signal

	def boll_out_of_band(self, close, bollbot, bolltop):
		if close is None or bollbot is None or bolltop is None:
			signal = 0
		else:
			if close < bollbot:
				signal = 1
			elif close > bolltop:
				signal = -1
			else:
				signal = 0

		return signal

	def cci(self, cci):
		if cci is None:
			signal = 0
		else:
			if cci < -100:
				signal = 1
			elif cci > 100:
				signal = -1
			else:
				signal = 0

		return signal

class daybot():

	def __init__(self, key, budget, symbol, period, format, live, debug, emailnotif = False):
		self.ts = None
		self.budget = budget
		self.cash = self.budget
		self.profit = None
		self.perf = None
		self.symbol = symbol
		self.period = period
		self.format = format
		self.live = live
		self.debug = debug
		self.close = None
		self.volume = None
		self.tstamp = None
		self.ts = TimeSeries(key=key, output_format='pandas')
		self.strategies = Strategies()
		self.signal = None
		self.nb_strategies = None
		self.vote = None
		self.buyprice = None
		self.sellprice = None
		self.totalbuysize = 0
		self.totalinvested = 0
		self.avgbuyprice = None
		self.totalprofit = 0
		self.position = 0
		self.emailnotif = emailnotif
		self.thread = threading.Thread(target = self.run_bot)
		self.logfile = datetime.now().strftime("%d_%m_%Y.log")
		self.logfile = "logs/" + self.symbol + "_" + self.logfile
		self.logger = self.setup_logger(self.symbol, self.logfile)
		self.logger.debug("=== %s LOGS %s===" % (self.symbol, datetime.now()))


	def notify_user(self, subject, body):
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.ehlo()
		server.starttls()
		server.login("amine.najahi@gmail.com", "bcyamsmgneicstpx")
		msg = "\r\n".join([
			"From: amine.najahi@gmail.com",
			"To: amine.najahi@gmail.com",
			"Subject: %s" % subject,
			"",
			"%s" % body,
			""
		])
		self.logger.debug("SEND EMAIL NOTIFICATION")
		server.sendmail("amine.najahi@gmail.com", "amine.najahi@gmail.com", msg)
		server.quit()

	def setup_logger(self, name, log_file, level=logging.DEBUG):
		log_setup = logging.getLogger(name)
		fileHandler = logging.FileHandler(log_file, mode='a')
		streamHandler = logging.StreamHandler()
		log_setup.setLevel(level)
		log_setup.addHandler(fileHandler)
		log_setup.addHandler(streamHandler)
		return log_setup

	def buy(self, riskfactor):
		self.buyprice = self.close
		self.buysize = self.cash * riskfactor / self.buyprice
		self.cash -= self.buysize * self.buyprice
		self.logger.debug("%s [%s] BUY %.2f SHARES @ %8.3f" % (self.tstamp, self.symbol, self.buysize, self.close))

		self.totalbuysize += self.buysize
		self.totalinvested += self.buysize * self.buyprice
		self.avgbuyprice = self.totalinvested / self.totalbuysize
		self.logger.debug("%s [%s] HAVE %.2f SHARES @ AVG %8.3f" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice))
		self.print_balance()

		self.position = 1

		if self.emailnotif:
			subject = "[%s] BUY %.2f SHARES @ %8.3f" % (self.symbol, self.buysize, self.close)
			body = "TIMESTAMP: %s\n" % self.tstamp
			body += "BUY %.2f SHARES @ %8.3f OF %s STOCK\n" % (self.buysize, self.close, self.symbol)
			body += "[SUMMARY] BUDGET = %.2f, CASH = %.2f$, INVESTED = %.2f, PROFIT/LOSS = %.2f$, PERF = %.2f%%" % (
				self.budget, self.cash, self.totalinvested, self.totalprofit, self.perf)
			self.notify_user(subject, body)

	def sell(self):
		self.sellprice = self.close
		self.sellsize = self.totalbuysize
		self.cash += self.sellsize * self.sellprice
		self.logger.debug("%s [%s] SELL %.2f SHARES @ %8.3f" % (self.tstamp, self.symbol, self.sellsize, self.sellprice))

		self.totalbuysize = 0
		self.totalinvested = 0
		self.profit = (self.sellprice - self.avgbuyprice) * self.sellsize
		self.totalprofit += self.profit
		self.logger.debug("%s [%s] SOLD %.2f SHARES @ %8.3f MADE %.3f$" % (self.tstamp, self.symbol, self.sellsize, self.sellprice, self.profit))
		self.print_balance()

		self.position = 0


		if self.emailnotif:
			subject = "[%s] SELL %.2f SHARES @ %8.3f" % (self.symbol, self.sellsize, self.close)
			body = "TIMESTAMP: %s\n" % self.tstamp
			body += "SELL %.2f SHARES @ %8.3f OF %s STOCK\n" % (self.sellsize, self.sellprice, self.symbol)
			body += "[SUMMARY] BUDGET = %.2f, CASH = %.2f$, INVESTED = %.2f, PROFIT/LOSS = %.2f$, PERF = %.2f%%" % (
				self.budget, self.cash, self.totalinvested, self.totalprofit, self.perf)
			self.notify_user(subject, body)

	def run_algo(self, tstamp, row):
		self.tstamp = tstamp
		self.close = row['4. close']
		self.volume = row['5. volume']
		self.macdhist = row['trend_macd_diff']
		self.macd = row['trend_macd']
		self.macd_signal = row['trend_macd_signal']
		self.rsi = row['momentum_rsi']
		self.cci = row['trend_cci']
		self.bolltop =row['volatility_bbh']
		self.bollbot = row['volatility_bbl']

		print("%s [%s] close %8.3f, volume %8d, macd %8.3f, macd_signal %8.3f, macdhist %8.3f, rsi %8.3f, cci %8.3f, bolltop %8.3f, bollbot %8.3f cci %3d" % (
			self.tstamp, self.symbol, self.close, self.volume, self.macd, self.macd_signal, self.macdhist, self.rsi, self.cci, self.bolltop, self.bollbot, self.cci))

		self.signal = 0
		self.nb_strategies = 0
		self.profit_loss_vote = 0
		self.macd_vote = 0
		self.rsi_vote = 0
		self.boll_vote = 0
		self.cci_vote = 0
		self.total_vote = 0

		self.profit_loss_vote = self.strategies.take_profit_stop_loss(self.close, self.buyprice)
		self.nb_strategies += 1

		self.macd_vote = self.strategies.macd_zero_crossing(self.macdhist)
		self.nb_strategies += 1

		self.rsi_vote = self.strategies.rsi_out_of_band(self.rsi)
		self.nb_strategies += 1

		self.boll_vote = self.strategies.boll_out_of_band(self.close, self.bollbot, self.bolltop)
		self.nb_strategies += 1

		self.cci_vote = self.strategies.cci(self.cci)
		self.nb_strategies += 1

		self.total_vote = self.profit_loss_vote + self.macd_vote + self.rsi_vote + self.boll_vote + self.cci_vote
		self.vote = self.total_vote / self.nb_strategies

		print("%s [%s] [%d/%d](%.2f) take_profit_stop_loss %3d, macd_zero_crossing %3d,  rsi_out_of_band %3d, boll_out_off_band %3d cci %3d" % (
				self.tstamp, self.symbol, self.total_vote, self.nb_strategies, self.vote, self.profit_loss_vote, self.macd_vote, self.rsi_vote, self.boll_vote, self.cci_vote))

		if self.vote >= 0.5 and self.position == 0:
			self.buy(0.5)
		elif self.vote <= -0.5 and self.position == 1 and self.close > self.avgbuyprice:
			self.sell()


	def get_market_data(self, debug=False):
		print("===GET MARKET DATA FOR %s===" % self.symbol)
		self.data, self.meta_data = self.ts.get_intraday(symbol=self.symbol, interval=str(self.period) + "min", outputsize=self.format)
		self.data = self.data.sort_index()
		if debug:
			print(self.data.tail(3))

		self.data = ta.utils.dropna(self.data)
		self.data = ta.add_all_ta_features(self.data, open="1. open", high="2. high", low="3. low", close="4. close", volume="5. volume", fillna=True)
		#if debug:
		#	print(self.data.tail(3))

		# max 5 api calls per minutes
		time.sleep(15)

		print("===GOT MARKET DATA FOR %s===" % self.symbol)
		return self.data

	def print_balance(self):
		self.perf = self.totalprofit / self.budget * 100
		self.logger.debug("%s [%s] BUDGET = %.2f, CASH = %.2f$, INVESTED = %.2f, PROFIT/LOSS = %.2f$, PERF = %.2f%%" % (
		self.tstamp, self.symbol, self.budget, self.cash, self.totalinvested, self.totalprofit, self.perf))

	def backtest(self):
		print("===BACKTEST FOR %s===" % self.symbol)
		now = datetime.now()
		dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
		print(dt_string)

		self.data = self.get_market_data(debug=self.debug)

		for index, row in self.data.iterrows():
			self.run_algo(index, row)

		self.print_balance()

	def livetest(self):
		print("===LIVETEST FOR %s===" % self.symbol)

		tsbefore = None
		tsnow = None
		while True :
			weekday = datetime.today().weekday()
			open = datetime.now().replace(hour=9, minute=30)
			close = datetime.now().replace(hour=16, minute=0)
			now = datetime.now()
			dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

			if weekday < 5 and now > open and now < close:
				lock.acquire()
				self.data = self.get_market_data(debug=self.debug)

				tsnow = self.data.tail(1).index[0]
				row = self.data.iloc[-1]
				if tsnow != tsbefore and tsbefore is not None:
					print("TIME LAPSE NOW:%s, BEFORE:%s" % (tsnow, tsbefore))
					print("===RUN ALGO FOR %s===" % (self.symbol))
					self.run_algo(tsnow, row)
					print("===RAN ALGO FOR %s===" % (self.symbol))

				tsbefore = tsnow
				lock.release()
			else:
				print("%s MARKET IS CLOSED..." % dt_string)

			time.sleep(self.period * 60)

	def run_bot(self):
		if self.live:
			self.livetest()
		else:
			self.backtest()

	def start_bot(self):
		self.thread.start()

if __name__ == '__main__':
	bots = []

	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_columns', None)
	pd.set_option('display.width', 1000)
	#register_matplotlib_converters()

	ap = argparse.ArgumentParser()
	ap.add_argument("-k", "--key", required=False, help="api key")
	ap.add_argument("-b", "--budget", required=False, help="allocated budget")
	ap.add_argument("-s", "--symbol", required=False, help="symbols to trade")
	ap.add_argument("-p", "--period", required=False, help="time interval in min 1, 5, 15, 60")
	ap.add_argument("-t", "--backtest", required=False, help="backtest")
	ap.add_argument("-e", "--emailnotif", required=False, help="emailnotif")
	args = vars(ap.parse_args())

	if args['key']:
		apikey = args['key']
	else:
		apikey = 'LCN3E4TILGN8BPA7'

	if args['budget']:
		budget = int(args['budget'])
	else:
		budget = 1000

	if args['symbol']:
		watchlist = args['symbol'].split(",")
	else:
		watchlist = ['AAPL','MSFT','TSLA', 'FB', 'INTC', 'QCOM']

	if args['period']:
		period = args['period']
	else:
		period = 15

	if args['backtest']:
		live = False
	else:
		live = True

	if args['emailnotif']:
		emailnotif = True
	else:
		emailnotif = False

	#live = False
	#watchlist = ['TSLA']
	#emailnotif = True
	for symbol in watchlist:
		print("CREATE BOT FOR %s" % symbol)
		bots.append(daybot(key='LCN3E4TILGN8BPA7', budget=budget, symbol=symbol, period=period, format="full", live=live, debug=True, emailnotif=emailnotif))
		time.sleep(3)

	for bot in bots:
		print("START BOT FOR %s" % bot.symbol)
		bot.start_bot()
		time.sleep(3)

	while True:
		time.sleep(60)

	print("END OF PROGRAM")