import threading
import smtplib
from datetime import datetime
from Market import Market
from MMStrategy import MMStrategy
from MyLogger import MyLogger
from Stock import Stock
import time

lock = threading.Lock()

class MMBot(object):

	def __init__(self, key, budget, symbol, period, live, debug, email = False, daily = False):
		self.data = None
		self.budget = budget
		self.cash = budget
		self.symbol = symbol
		self.period = period
		self.daily = daily
		self.live = live
		self.debug = debug
		self.email = email
		self.riskfactor = 0.5
		self.signal = 0
		self.market = Market(key)
		self.strategy = MMStrategy()
		self.mylogger = MyLogger(symbol)
		self.stock = Stock(symbol, self.mylogger)
		self.thread = threading.Thread(target = self.run_bot)
		self.BUY = 1
		self.SELL = -1
		self.HOLD = 0


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
		self.mylogger.logger.debug("SEND EMAIL NOTIFICATION")
		server.sendmail("amine.najahi@gmail.com", "amine.najahi@gmail.com", msg)
		server.quit()

	def print_balance(self):
		self.stock.potentialvalue = self.stock.totalbuysize * self.stock.close
		self.stock.potentialprofit = (self.stock.close - self.stock.avgbuyprice) * self.stock.totalbuysize
		self.stock.potentialperf = self.stock.potentialprofit / self.budget * 100
		self.stock.perf = self.stock.totalprofit / self.budget * 100

		if self.stock.inmarket != 0 and self.stock.outmarket != 0:
			self.stock.marketratio = self.stock.inmarket / (self.stock.inmarket + self.stock.outmarket) * 100
		else:
			self.stock.marketratio = 0

		self.mylogger.logger.debug("[%8s] BUDGET = %6.2f, IN MARKET = %3d, OUT MARKET = %3d, MARKET RATIO = %3d%%, #TRANSAC = %2d, CASH = %06.2f, INVESTED = %06.2f, POT VALUE = %06.2f, POT PROFIT = %6.2f,  POT PERF = %5.2f%%, REAL PROFIT/LOSS = %6.2f, REAL PERF = %5.2f%%" % (
				self.stock.symbol, self.budget, self.stock.inmarket, self.stock.outmarket, self.stock.marketratio,
				self.stock.transaction, self.cash, self.stock.totalinvested, self.stock.potentialvalue, self.stock.potentialprofit, self.stock.potentialperf, self.stock.totalprofit, self.stock.perf))

	def buy(self):
		self.stock.buy(self.riskfactor, self.cash)
		self.cash -= self.stock.buysize * self.stock.buyprice
		self.print_balance()

		if self.email:
			subject = "[%s] BUY %.2f SHARES @ %8.3f" % (self.stock.symbol, self.stock.buysize, self.stock.close)
			body = "TIMESTAMP: %s\n" % self.stock.tstamp
			body += "BUY %.2f SHARES @ %8.3f OF %s STOCK\n" % (self.stock.buysize, self.stock.close, self.stock.symbol)
			self.notify_user(subject, body)

	def sell(self):

		self.stock.sell()
		self.cash += self.stock.sellsize * self.stock.sellprice
		self.print_balance()

		if self.email:
			subject = "[%s] SELL %.2f SHARES @ %8.3f" % (self.stock.symbol, self.stock.sellsize, self.stock.close)
			body = "TIMESTAMP: %s\n" % self.stock.tstamp
			body += "SELL %.2f SHARES @ %8.3f OF %s STOCK\n" % (self.stock.sellsize, self.stock.sellprice, self.stock.symbol)
			self.notify_user(subject, body)

	def run_algo(self, index, row):

		signal = self.strategy.run_strategy(index, row, self.stock)

		if signal == self.BUY:
			if self.stock.close < self.stock.avgbuyprice and self.cash >= self.stock.close:
				self.buy()
			elif self.stock.avgbuyprice == 0:
				self.buy()

		elif signal == self.SELL:
			if self.stock.position == 1:
				self.sell()

		self.stock.updatemarketcounter()

	def backtest(self):
		print("===BACKTEST FOR %s===" % self.stock.symbol)

		now = datetime.now()
		dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
		print(dt_string)

		lock.acquire()
		self.data = self.market.getData(self.stock.symbol, self.period, self.daily, debug=self.debug)
		lock.release()

		for index, row in self.data.iterrows():
			self.stock.tstamp = index
			self.stock.close = row['4. close']
			self.stock.volume = row['5. volume']
			self.run_algo(index, row)


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
				self.data = self.market.getData(self.stock.symbol, self.period, self.daily, debug=self.debug)

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

	def stop_bot(self):
		self.thread.join()
