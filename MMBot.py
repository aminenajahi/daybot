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

	def __init__(self, budget, symbol, period, live, debug, since, broker, mylogger, email=False, daily=False,liquidate=False):
		self.data = None
		self.botname = "MMBot"
		self.budget = budget
		self.symbol = symbol
		self.period = int(period)
		self.daily = daily
		self.live = live
		self.debug = debug
		self.email = email
		self.since = since
		self.liquidate=liquidate
		self.buyriskfactor = 0.5
		self.minbuychange = 0.97
		self.sellriskfactor = 1
		self.minsellchange = 1.01
		self.signal = 0
		self.mylogger = mylogger
		self.market = Market()
		self.strategy = MMStrategy(mylogger)
		self.broker = broker
		self.stock = Stock(symbol, self.mylogger, self.broker)
		self.thread = threading.Thread(target = self.run_bot)
		self.BUY = -1
		self.SELL = 1
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

		cash_to_invest = self.broker.cash * self.buyriskfactor
		nb_shares_to_buy = math.floor(cash_to_invest / self.stock.close)

		self.mylogger.logger.debug(
			"%s [%s] BUY OPPORTUNITY @ %8.3f$, VOTED @ %8.3f, BUYING %d SHARES AMOUNTING %8.3f$" % (
			self.stock.tstamp, self.stock.symbol, self.stock.close, self.vote, nb_shares_to_buy, cash_to_invest))

		if cash_to_invest <= 0:
			self.mylogger.logger.debug("%s [%s] NOT ENOUGH MONEY, CASH %8.2f" % (self.stock.tstamp, self.symbol, cash_to_invest))
			return

		if cash_to_invest > self.budget:
			self.mylogger.logger.debug("%s [%s] OVER BUDGET, CASH %8.2f$ BUDGET %8.2f" % (self.stock.tstamp, self.symbol, cash_to_invest, self.budget))
			return

		if cash_to_invest < self.budget * 0.25:
			self.mylogger.logger.debug("%s [%s] INVESTING REMAINING BUDGET OF %8.3f$" % (self.stock.tstamp, self.symbol, cash_to_invest))
			cash_to_invest = self.broker.cash

		if nb_shares_to_buy <= 0:
			self.mylogger.logger.debug("%s [%s] INVALID NUMBER OF SHARES TO BUY %d" % (self.stock.tstamp, self.symbol, nb_shares_to_buy))
			return

		if self.broker.totalinvested + cash_to_invest > self.broker.totalbudget:
			self.mylogger.logger.debug("%s [%s] TOTAL INVESTMENT %8.2f$ IS OVER TOTAL BUDGET OF %.3f$" % (self.stock.tstamp, self.symbol, self.broker.totalinvested + cash_to_invest, self.broker.totalbudget))
			return

		nb_share_before = self.stock.totalbuysize
		price_before = self.stock.avgbuyprice

		result = self.broker.buy_shares(self.stock, nb_shares_to_buy)
		if result is not 0:
			return

		self.broker.calculate_profit(self.stock)
		self.broker.print_balance(self.stock)

		if self.email and result >= 0:
			subject = "[%s] [%s] BUY %.2f SHARES @ %8.3f" % (self.botname, self.stock.symbol, self.stock.buysize, self.stock.close)
			body = "TIMESTAMP: %s\n" % self.stock.tstamp
			body += "YOU HAVE %.2f SHARES @ AVG %8.3f OF %s STOCK\n" % (nb_share_before, price_before, self.stock.symbol)
			body += "WILL BUY %.2f SHARES @ %8.3f OF %s STOCK\n" % (nb_shares_to_buy, self.stock.close, self.stock.symbol)
			body += "adx %8.3f, sma20 %8.3f, sma50 %8.3f, sma100 %8.3f " % (self.strategy.adx, self.strategy.sma20, self.strategy.sma50, self.strategy.sma100)
			body += "rsi %8.3f, cci %8.3f, stoch %8.3f " % (self.strategy.rsi, self.strategy.cci, self.strategy.stoch)
			body += "trend_dir %d, trend_str %d, rsi_vote %d, cci_vote %d, stoch_vote %d" % (self.strategy.trend_dir, self.strategy.trend_str, self.strategy.rsi_vote, self.strategy.cci_vote,self.strategy.stoch_vote)
			self.__notify_user(subject, body)

	def __sell(self):

		nb_shares_to_sell = math.floor(self.stock.totalbuysize * self.sellriskfactor)

		self.mylogger.logger.debug(
			"\n%s [%s] SELL OPPORTUNITY @ %8.3f$, VOTED @ %8.3f, SELLING %d SHARES" % (
			self.stock.tstamp, self.stock.symbol, self.stock.close, self.vote, nb_shares_to_sell))

		if nb_shares_to_sell <= 0:
			self.mylogger.logger.debug("%s [%s] INVALID NUMBER OF SHARES TO SELL %d" % (self.stock.tstamp, self.symbol, nb_shares_to_sell))
			return

		if nb_shares_to_sell * self.stock.close < self.budget * 0.25:
			self.mylogger.logger.debug("%s [%s] SELLING REMAINING SHARES %d" % (self.stock.tstamp, self.symbol, nb_shares_to_sell * self.stock.close))
			nb_shares_to_sell = self.stock.totalbuysize

		nb_share_before = self.stock.totalbuysize
		price_before = self.stock.avgbuyprice

		result = self.broker.sell_shares(self.stock, nb_shares_to_sell)

		self.broker.calculate_profit(self.stock)
		self.broker.print_balance(self.stock)
		self.mylogger.logger.debug("%s [%s] BROKER HAS %8.3f, RISK FACTOR %8.2f" % (self.stock.tstamp, self.symbol, self.broker.cash, self.buyriskfactor))

		if self.email and nb_shares_to_sell > 0 and result >= 0:
			subject = "[%s] [%s] SELL %.2f SHARES @ %8.3f" % (self.botname, self.stock.symbol, self.stock.sellsize, self.stock.close)
			body = "TIMESTAMP: %s\n" % self.stock.tstamp
			body += "YOU HAVE %.2f SHARES @ AVG %8.3f OF %s STOCK\n" % (nb_share_before, price_before, self.stock.symbol)
			body += "WILL SELL %.2f SHARES @ %8.3f OF %s STOCK\n" % (nb_shares_to_sell, self.stock.close, self.stock.symbol)
			body += "TRANSACTION PROFIT OF %.2f$ (%.2f%%)\n" % (self.stock.profit, self.stock.profitpercent)
			body += "adx %8.3f, sma20 %8.3f, sma50 %8.3f, sma100 %8.3f\n" % (self.strategy.adx, self.strategy.sma20, self.strategy.sma50, self.strategy.sma100)
			body += "rsi %8.3f, cci %8.3f, stoch %8.3f\n" % (self.strategy.rsi, self.strategy.cci, self.strategy.stoch)
			body += "trend_dir %d, trend_str %d, rsi_vote %d, cci_vote %d, stoch_vote %d\n" % (self.strategy.trend_dir, self.strategy.trend_str, self.strategy.rsi_vote, self.strategy.cci_vote,self.strategy.stoch_vote)
			self.__notify_user(subject, body)

	def __run_algo(self, index, row):

		self.mylogger.logger.debug("\n%s [%s] RUN ALGO" % (self.stock.tstamp, self.symbol))
		self.stock.updatemarketcounter()

		signal, self.vote = self.strategy.run_strategy(index, row, self.stock)

		if signal == self.BUY:
			if self.stock.close < self.stock.avgbuyprice * self.minbuychange or self.stock.totalbuysize <= 0:
				self.__buy()

		#only SELL if we made money.
		elif signal == self.SELL:
			if self.stock.close > self.stock.avgbuyprice * self.minsellchange and self.stock.totalbuysize > 0:
				self.__sell()

		return signal, self.vote

	def __backtest(self):
		print("===BACKTEST FOR %s===" % self.stock.symbol)

		now = datetime.now()
		dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
		print(dt_string)

		lock.acquire()

		if self.daily == True:
			self.dailydata = self.market.getDailyData(self.stock.symbol, self.since, debug=self.debug)
			if self.dailydata is not None:
				for index, row in self.dailydata.iterrows():
					self.stock.tstamp = index
					self.stock.close = row['4. close']
					self.stock.volume = row['5. volume']
					signal, vote = self.__run_algo(index, row)
		else:
			self.intradata = self.market.getIntraDayData(self.stock.symbol, self.since, self.period, debug=self.debug)
			if self.intradata is not None:
				for index, row in self.intradata.iterrows():
					self.stock.tstamp = index
					self.stock.close = row['4. close']
					self.stock.volume = row['5. volume']
					signal, vote = self.__run_algo(index, row)

		lock.release()

	def __livetest(self):
		print("===LIVETEST FOR %s===" % self.symbol)

		tsbefore = None
		tsnow = None
		while True :

			now = datetime.now()
			dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

			if self.market.isOpen(now) == True:
				if self.stock.transaction > 0 and self.stock.totalbuysize == 0 and self.liquidate is not None and self.liquidate == 1:
					self.mylogger.logger.debug("%s [%s] LIQUIDATING STOCK STOPPING BOT" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.stock.symbol))
					return;

				lock.acquire()
				self.data = None
				while self.data is None:
					#if self.market.isOpen(now) == False:
					#	break;

					if self.daily == True:
						self.data = self.market.getDailyData(self.stock.symbol, self.since, debug=self.debug)
					else:
						self.data = self.market.getIntraDayData(self.stock.symbol, self.since, self.period, debug=self.debug)

				if self.data is not None:
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
				self.mylogger.logger.debug("%s [%s] MARKET IS CLOSED..." % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.stock.symbol))
				if self.market.isPostClose(now):
					self.mylogger.logger.debug("%s [%s] DAY IS DONE..." % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.stock.symbol))
					return;

			#wait for the beginning of the next sample period
			self.mylogger.logger.debug("%s [%s] NEXT SAMPLE IN %d min" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.stock.symbol, self.period - (datetime.now().minute % self.period)))
			while datetime.now().minute % self.period != 0:
				time.sleep(30)

	def run_bot(self):
		if self.live:
			self.__livetest()
		else:
			self.__backtest()

	def start_bot(self):
		self.thread.start()

	def stop_bot(self):
		self.thread.join()
