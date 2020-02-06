import threading
import smtplib
from datetime import datetime
from Market import Market
from SimpleStrategy import SimpleStrategy
from MyLogger import MyLogger
from Stock import Stock

lock = threading.Lock()

class SimpleBot(object):

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
		self.riskfactor = 1
		self.signal = 0
		self.market = Market(key)
		self.strategy = SimpleStrategy()
		self.mylogger = MyLogger(symbol)
		self.stock = Stock(symbol, self.mylogger)
		self.thread = threading.Thread(target = self.run_bot)


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

		if signal == 1:
			self.buy()
		elif signal == -1:
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

	def run_bot(self):
		self.backtest()

	def start_bot(self):
		self.thread.start()

	def stop_bot(self):
		self.thread.join()
