import threading
import smtplib
from datetime import datetime
from Market import Market
from MMStrategy import MMStrategy
from MyLogger import MyLogger
from Stock import Stock
from Broker import Broker
from IBBroker import IBBroker
import time
import math as math


lock = threading.Lock()

class MMBot(object):

	def __init__(self, key, budget, symbol, period, live, debug, since, email=False, daily=False, ibk=False):
		self.data = None
		self.botname = "MMBot"
		self.budget = budget
		self.symbol = symbol
		self.period = int(period)
		self.daily = daily
		self.live = live
		self.debug = debug
		self.email = email
		self.key = key
		self.since = since
		self.buyriskfactor = 0.3
		self.sellriskfactor = 0.5
		self.signal = 0
		self.market = Market(key)
		self.strategy = MMStrategy()
		self.mylogger = MyLogger(symbol)
		self.stock = Stock(symbol, self.mylogger)

		if ibk == False:
			print("Create normal broker")
			self.broker = Broker(budget, self.mylogger)
		else:
			print("Create IBK broker")
			self.broker = IBBroker(budget, self.mylogger)

		self.thread = threading.Thread(target = self.run_bot)
		self.BUY = 1
		self.SELL = -1
		self.HOLD = 0


	def __notify_user(self, subject, body):
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
		self.mylogger.logger.debug("SEND EMAIL NOTIFICATION")
		server.sendmail("amine.najahi@gmail.com", "amine.najahi@gmail.com", msg)
		server.quit()

	def print_balance(self):
		self.broker.print_balance(self.stock)

	def __buy(self):

		#cash_to_invest = (self.broker.cash + self.broker.invested) * self.buyriskfactor
		#cash_to_invest = (self.broker.cash + self.broker.invested) * self.buyriskfactor * self.vote
		#cash_to_invest = self.broker.cash * self.buyriskfactor * self.vote
		cash_to_invest = self.broker.cash * self.vote
		self.mylogger.logger.debug(
			"\n%s [%s] BUY OPPORTUNITY @ %8.3f EVALUATED @ %8.3f INVEST %8.3f" % (
			self.stock.tstamp, self.stock.symbol, self.stock.close, self.vote, cash_to_invest))

		self.broker.buy_dollar_amount(self.stock, cash_to_invest)
		self.broker.print_balance(self.stock)

		if self.email:
			subject = "[%s] [%s] BUY %.2f SHARES @ %8.3f" % (self.botname, self.stock.symbol, self.stock.buysize, self.stock.close)
			body = "TIMESTAMP: %s\n" % self.stock.tstamp
			body += "HAVE %.2f SHARES @ AVG %8.3f OF %s STOCK\n" % (self.stock.totalbuysize, self.stock.avgbuyprice, self.stock.symbol)
			body += "BUY %.2f SHARES @ %8.3f OF %s STOCK\n" % (self.stock.buysize, self.stock.close, self.stock.symbol)
			self.__notify_user(subject, body)

	def __sell(self):

		#nb_shares_to_sell = math.floor(self.stock.totalbuysize * self.sellriskfactor * self.vote)
		#nb_shares_to_sell = math.floor(self.stock.totalbuysize * self.sellriskfactor)
		nb_shares_to_sell = math.floor(self.stock.totalbuysize * self.vote)
		self.mylogger.logger.debug(
			"\n%s [%s] SELL OPPORTUNITY @ %8.3f EVALUATED @ %8.3f LIQUIDATE %8.3f SHARES" % (
			self.stock.tstamp, self.stock.symbol, self.stock.close, self.vote, nb_shares_to_sell))

		self.broker.sell_shares(self.stock, nb_shares_to_sell)
		self.broker.print_balance(self.stock)

		if self.email:
			subject = "[%s] [%s] SELL %.2f SHARES @ %8.3f" % (self.botname, self.stock.symbol, self.stock.sellsize, self.stock.close)
			body = "TIMESTAMP: %s\n" % self.stock.tstamp
			body += "HAVE %.2f SHARES @ AVG %8.3f OF %s STOCK\n" % (self.stock.totalbuysize, self.stock.avgbuyprice, self.stock.symbol)
			body += "SELL %.2f SHARES @ %8.3f OF %s STOCK\n" % (self.stock.sellsize, self.stock.sellprice, self.stock.symbol)
			self.__notify_user(subject, body)

	def __run_algo(self, index, row):

		signal, self.vote = self.strategy.run_strategy(index, row, self.stock)

		if signal == self.BUY:
			if self.stock.close < self.stock.avgbuyprice or self.stock.avgbuyprice == 0:
				self.__buy()
		elif signal == self.SELL:
			#if self.stock.close > self.stock.avgbuyprice and self.stock.totalbuysize > 0:
			if self.stock.close > self.stock.avgbuyprice:
				self.__sell()

		self.stock.updatemarketcounter()

	def __backtest(self):
		print("===BACKTEST FOR %s===" % self.stock.symbol)

		now = datetime.now()
		dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
		print(dt_string)

		lock.acquire()
		if self.daily == True:
			self.data = self.market.getDailyData(self.stock.symbol, self.since, debug=self.debug)
		else:
			self.data = self.market.getIntraDayData(self.stock.symbol, self.period, debug=self.debug)
		lock.release()

		for index, row in self.data.iterrows():
			self.stock.tstamp = index
			self.stock.close = row['4. close']
			self.stock.volume = row['5. volume']
			self.__run_algo(index, row)


	def __livetest(self):
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
				if self.daily == True:
					self.data = self.market.getDailyData(self.stock.symbol, "2019-06-01", debug=self.debug)
				else:
					self.data = self.market.getIntraDayData(self.stock.symbol, self.period, debug=self.debug)

				tsnow = self.data.tail(1).index[0]
				row = self.data.iloc[-1]
				if tsnow != tsbefore:
					self.stock.tstamp = tsnow
					self.stock.close = row['4. close']
					self.stock.volume = row['5. volume']
					self.__run_algo(tsnow, row)

				tsbefore = tsnow
				lock.release()
			else:
				print("%s MARKET IS CLOSED..." % dt_string)

			time.sleep(self.period * 60)

	def run_bot(self):
		if self.live:
			self.__livetest()
		else:
			self.__backtest()

	def start_bot(self):
		self.thread.start()

	def stop_bot(self):
		self.thread.join()
