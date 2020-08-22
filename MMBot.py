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
import signal
from matplotlib import pyplot
import numpy as np
import pandas as pd

lock = threading.BoundedSemaphore(10)

class MMBot(object):

	def __init__(self, budget, symbol, period, live, debug, since, broker,  market, mylogger, email=False, daily=False,liquidate=False):
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
		self.sellriskfactor = 0.5
		self.signal = 0
		self.mylogger = mylogger
		self.market = market
		self.strategy = MMStrategy(mylogger)
		self.broker = broker
		self.stock = Stock(symbol, self.mylogger, self.broker)
		self.thread = threading.Thread(target = self.run_bot)
		self.BUY = -1
		self.SELL = 1
		self.HOLD = 0
		self.exit = False

		signal.signal(signal.SIGINT, self.sighandler)

	def sighandler(self, signum, frame):
		self.exit = True

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
		self.broker.print_transactions(self.stock)
		self.broker.print_balance(self.stock)

	def plot_data(self):
		print("plot data")
		
		#buy_df = self.broker.tx.loc[self.broker.tx['ACTION'] == "BUY"]
		#print(buy_df[['TS','ACTION','SYMBOL','C',"SHARES"]])

		#sell_df = self.broker.tx.loc[self.broker.tx['ACTION'] == "SELL"]
		#print(sell_df[['TS','ACTION','SYMBOL','C',"SHARES"]])
		
		#buy_df.index = pd.to_datetime(buy_df['TS'])
		#print(buy_df[['ACTION','SYMBOL','C',"SHARES"]])

		#sell_df.index = pd.to_datetime(sell_df['TS'])
		#print(sell_df[['ACTION','SYMBOL','C',"SHARES"]])
		
		#self.data = pd.merge(self.data, buy_df['ACTION'], left_index=True, right_index=True, how='inner')
		#self.data = pd.merge(self.data, sell_df['ACTION'], left_index=True, right_index=True, how='inner')
		#self.data.head()
	
		self.data.index = range(0,len(self.data))
		fig, ax = pyplot.subplots(5)
		title = "Stock Price " + self.symbol

		#buy_df = self.data.loc[self.data['ACTION'] == "BUY"]
		#buy_mark = list(buy_df.index)
		#print(buy_mark)

		#sell_df = self.data.loc[self.data['ACTION'] == "SELL"]
		#sell_mark = list(sell_df.index)
		#print(sell_mark)
		
		ax[0].plot(self.data.index, self.data[['C','mvwap']])
		ax[0].set(xlabel='Tick', ylabel='Price $', title=title)

		ax[1].plot(self.data.index, self.data[['momentum_rsi']])
		ax[1].set(xlabel='Tick', ylabel='Index', title="RSI")

		ax[2].plot(self.data.index, self.data[['momentum_stoch_signal']])
		ax[2].set(xlabel='Tick', ylabel='Index', title="Stoch RSI")

		ax[3].plot(self.data.index, self.data[['trend_cci']])
		ax[3].set(xlabel='Tick', ylabel='Index', title="CCI")

		ax[4].plot(self.data.index, self.data[['trend_adx']])
		ax[4].set(xlabel='Tick', ylabel='Index', title="Trend")

		#ax[6].plot(self.data.index, self.data[['action']])
		#ax[6].set(xlabel='Tick', ylabel='BUY/SELL', title="Action")
		
		#x[7].plot(self.data.index, self.data[['C']], marker="^", markevery=buy_mark)
		#x[7].plot(self.data.index, self.data[['C']], marker="v", markevery=sell_mark)
		#x[7].set(xlabel='Tick', ylabel='Price $', title=title)


		pyplot.show()

	def __buy(self, buyriskfactor):

		cash_to_invest = self.broker.cash * buyriskfactor
		#cash_to_invest = self.budget * self.buyriskfactor
		nb_shares_to_buy = math.floor(cash_to_invest / self.stock.close)

		self.mylogger.logger.debug(
			"%s [%s] BUY LONG OPPORTUNITY @ %8.3f$, VOTED @ %8.3f, BUYING %d SHARES AMOUNTING %8.3f$" % (
			self.stock.tstamp, self.stock.symbol, self.stock.close, self.vote, nb_shares_to_buy, cash_to_invest))

		self.mylogger.logger.debug(
			"%s [%s] BUDGET %8.2f$, INVESTED %8.2f$, TOTAL BUDGET %.3f$" % (
			self.stock.tstamp, self.symbol, self.budget, Broker.totalinvested, self.broker.totalbudget))
			
		if cash_to_invest <= 0:
			self.mylogger.logger.debug("%s [%s] NOT ENOUGH MONEY, CASH %8.2f" % (self.stock.tstamp, self.symbol, cash_to_invest))
			return

		if Broker.totalinvested + cash_to_invest > self.budget:
			self.mylogger.logger.debug("%s [%s] OVER BUDGET, CASH %8.2f$ BUDGET %8.2f" % (self.stock.tstamp, self.symbol, Broker.totalinvested + cash_to_invest, self.budget))
			return

		if cash_to_invest < self.budget * 0.25:
			self.mylogger.logger.debug("%s [%s] INVESTING REMAINING BUDGET OF %8.3f$" % (self.stock.tstamp, self.symbol, cash_to_invest))
			cash_to_invest = self.broker.cash

		if nb_shares_to_buy <= 0:
			self.mylogger.logger.debug("%s [%s] INVALID NUMBER OF SHARES TO BUY %d" % (self.stock.tstamp, self.symbol, nb_shares_to_buy))
			return

		if Broker.totalinvested + cash_to_invest > self.broker.totalbudget:
			self.mylogger.logger.debug("%s [%s] TOTAL INVESTMENT %8.2f$ IS OVER TOTAL BUDGET OF %.3f$" % (self.stock.tstamp, self.symbol, Broker.totalinvested + cash_to_invest, self.broker.totalbudget))
			return

		nb_share_before = self.stock.totalbuysize
		price_before = self.stock.avgbuyprice

		if self.market.isOpen(datetime.now()) == True:
			result = self.broker.buy_shares(self.stock, nb_shares_to_buy)
		elif (self.market.isPreOpen(datetime.now()) == True and self.market.rth == False) or (self.market.isPostClose(datetime.now()) == True and self.market.rth == False):			
			result = self.broker.buy_shares(self.stock, nb_shares_to_buy, price=self.stock.close)

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

	def __sell(self, sellriskfactor):

		#sell long position

		nb_shares_to_sell = math.floor(self.stock.totalbuysize * sellriskfactor)

		self.mylogger.logger.debug(
			"\n%s [%s] SELL LONG OPPORTUNITY @ %8.3f$, VOTED @ %8.3f, SELLING %d SHARES" % (
			self.stock.tstamp, self.stock.symbol, self.stock.close, self.vote, nb_shares_to_sell))

		if nb_shares_to_sell <= 0:
			self.mylogger.logger.debug("%s [%s] INVALID NUMBER OF SHARES TO SELL %d" % (self.stock.tstamp, self.symbol, nb_shares_to_sell))
			return

		if nb_shares_to_sell * self.stock.close < self.budget * 0.25:
			self.mylogger.logger.debug("%s [%s] SELLING REMAINING SHARES %d" % (self.stock.tstamp, self.symbol, nb_shares_to_sell * self.stock.close))
			nb_shares_to_sell = self.stock.totalbuysize

		nb_share_before = self.stock.totalbuysize
		price_before = self.stock.avgbuyprice

		if self.market.isOpen(datetime.now()) == True:
			result = self.broker.sell_shares(self.stock, nb_shares_to_sell)
		elif (self.market.isPreOpen(datetime.now()) == True and self.market.rth == False) or (self.market.isPostClose(datetime.now()) == True and self.market.rth == False):			
			result = self.broker.sell_shares(self.stock, nb_shares_to_sell, price=self.stock.close)

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

	def __buy_short(self, buyriskfactor):
		cash_to_invest = self.broker.cash * buyriskfactor
		nb_shares_to_short = math.floor(cash_to_invest / self.stock.close)

		self.mylogger.logger.debug(
			"%s [%s] BUY SHORT OPPORTUNITY @ %8.3f$, VOTED @ %8.3f, BUYING %d SHARES AMOUNTING %8.3f$" % (
			self.stock.tstamp, self.stock.symbol, self.stock.close, self.vote, nb_shares_to_short, cash_to_invest))

		self.mylogger.logger.debug(
			"%s [%s] BUDGET %8.2f$, INVESTED %8.2f$, TOTAL BUDGET %.3f$" % (
			self.stock.tstamp, self.symbol, self.budget, Broker.totalinvested, self.broker.totalbudget))
			
		if cash_to_invest <= 0:
			self.mylogger.logger.debug("%s [%s] NOT ENOUGH MONEY, CASH %8.2f" % (self.stock.tstamp, self.symbol, cash_to_invest))
			return

		if Broker.totalinvested + cash_to_invest > self.budget:
			self.mylogger.logger.debug("%s [%s] OVER BUDGET, CASH %8.2f$ BUDGET %8.2f" % (self.stock.tstamp, self.symbol, Broker.totalinvested + cash_to_invest, self.budget))
			return

		if cash_to_invest < self.budget * 0.25:
			self.mylogger.logger.debug("%s [%s] INVESTING REMAINING BUDGET OF %8.3f$" % (self.stock.tstamp, self.symbol, cash_to_invest))
			cash_to_invest = self.broker.cash

		if nb_shares_to_short < 0:
			self.mylogger.logger.debug("%s [%s] INVALID NUMBER OF SHARES TO SHORT %d" % (self.stock.tstamp, self.symbol, nb_shares_to_short))
			return

		if Broker.totalinvested + cash_to_invest > self.broker.totalbudget:
			self.mylogger.logger.debug("%s [%s] TOTAL INVESTMENT %8.2f$ IS OVER TOTAL BUDGET OF %.3f$" % (self.stock.tstamp, self.symbol, Broker.totalinvested + cash_to_invest, self.broker.totalbudget))
			return

		nb_share_before = self.stock.totalbuysize
		price_before = self.stock.avgbuyprice

		result = self.broker.buy_short_shares(self.stock, nb_shares_to_short)
		if result is not 0:
			return

		self.broker.calculate_profit(self.stock)
		self.broker.print_balance(self.stock)

		if self.email and result >= 0:
			subject = "[%s] [%s] BUY %.2f SHARES @ %8.3f" % (self.botname, self.stock.symbol, self.stock.buysize, self.stock.close)
			body = "TIMESTAMP: %s\n" % self.stock.tstamp
			body += "YOU HAVE %.2f SHARES @ AVG %8.3f OF %s STOCK\n" % (nb_share_before, price_before, self.stock.symbol)
			body += "WILL SHORT %.2f SHARES @ %8.3f OF %s STOCK\n" % (nb_shares_to_short, self.stock.close, self.stock.symbol)
			body += "adx %8.3f, sma20 %8.3f, sma50 %8.3f, sma100 %8.3f " % (self.strategy.adx, self.strategy.sma20, self.strategy.sma50, self.strategy.sma100)
			body += "rsi %8.3f, cci %8.3f, stoch %8.3f " % (self.strategy.rsi, self.strategy.cci, self.strategy.stoch)
			body += "trend_dir %d, trend_str %d, rsi_vote %d, cci_vote %d, stoch_vote %d" % (self.strategy.trend_dir, self.strategy.trend_str, self.strategy.rsi_vote, self.strategy.cci_vote,self.strategy.stoch_vote)
			self.__notify_user(subject, body)

	def __sell_short(self, sellriskfactor):

		nb_shares_to_sell = math.floor(self.stock.totalbuysize * sellriskfactor)

		self.mylogger.logger.debug(
			"\n%s [%s] SELL SHORT OPPORTUNITY @ %8.3f$, VOTED @ %8.3f, SELLING %d SHARES" % (
			self.stock.tstamp, self.stock.symbol, self.stock.close, self.vote, nb_shares_to_sell))

		if nb_shares_to_sell <= 0:
			self.mylogger.logger.debug("%s [%s] INVALID NUMBER OF SHARES TO SELL %d" % (self.stock.tstamp, self.symbol, nb_shares_to_sell))
			return

		if nb_shares_to_sell * self.stock.close < self.budget * 0.25:
			self.mylogger.logger.debug("%s [%s] SELLING REMAINING SHARES %d" % (self.stock.tstamp, self.symbol, nb_shares_to_sell * self.stock.close))
			nb_shares_to_sell = self.stock.totalbuysize

		nb_share_before = self.stock.totalbuysize
		price_before = self.stock.avgbuyprice

		result = self.broker.sell_short_shares(self.stock, nb_shares_to_sell)

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
		self.stock.updatemarketcounter(row)

		# set minimum price variation before buying or selling.
		#self.atr = row['volatility_atr'];
		#self.minbuychange = self.stock.avgbuyprice - self.atr * 3;
		#self.minsellchange = self.stock.avgbuyprice + self.atr * 3;
		#self.mylogger.logger.debug("PRICE THRESHOLDS: ATR:%.3f, CLOSE:%.2f, AVG:%.2f, BUY:%.2f, SELL:%.2f" % (self.atr, self.stock.close, self.stock.avgbuyprice, self.minbuychange, self.minsellchange))

		signal, self.vote, riskfactor, position = self.strategy.run_strategy(index, row, self.stock)

		if signal == self.BUY:
			if position == self.strategy.LONG:
				self.__buy(riskfactor)
			elif position == self.strategy.SHORT:
				self.__buy_short(riskfactor)

			return self.BUY

		elif signal == self.SELL:
			if position == self.strategy.LONG:
				self.__sell(riskfactor)
			elif position == self.strategy.SHORT:
				self.__sell_short(riskfactor)

			return self.SELL
			
		return self.HOLD

	def __backtest(self):
		print("===BACKTEST FOR %s===" % self.stock.symbol)

		now = datetime.now()
		dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
		print(dt_string)
		

		lock.acquire()
		
		if self.daily == True:
			self.data = self.market.getDailyData(self.stock.symbol, self.since, debug=self.debug)
		else:
			self.data = self.market.getIntraDayData(self.stock.symbol, self.since, self.period, self.live, debug=self.debug)

		
		if self.data is not None:
			for index, row in self.data.iterrows():
				self.stock.tstamp = index
				self.stock.close = row['C']
				self.stock.volume = row['V']
				action = self.__run_algo(index, row)
				#print(row)
					
		lock.release()
		#self.mylogger.logger.debug(self.data)

	def __livetest(self):
		print("===LIVETEST FOR %s===" % self.symbol)

		tsbefore = None
		tsbefore = None
		tsnow = None
		while self.exit == False:
			now = datetime.now()
			dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

			if self.market.isOpen(now) == True or (self.market.isPreOpen(now) == True and self.market.rth == False) or (self.market.isPostClose(now) == True and self.market.rth == False):			
				
				#lock.acquire()
				self.data = None
				while self.data is None:
					if self.daily == True:
						self.data = self.market.getDailyData(self.stock.symbol, self.since, debug=self.debug)
					else:
						self.data = self.market.getIntraDayData(self.stock.symbol, self.since, self.period, self.live, debug=self.debug)
				#lock.release()

				if self.data is not None:
					tsnow = self.data.tail(1).index[0]
					row = self.data.iloc[-1]

					if tsnow != tsbefore:
						self.stock.tstamp = tsnow
						self.stock.close = row['C']
						self.stock.volume = row['V']
						self.__run_algo(tsnow, row)

					tsbefore = tsnow
	
			else:
				self.mylogger.logger.debug("%s [%s] MARKET IS CLOSED, PREMARKET:%d, POSTMARKET:%d, RTH:%d..." % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.stock.symbol, self.market.isPreOpen(now), self.market.isPostClose(now), self.market.rth))
			
			#wait for the beginning of the next sample period
			nextinterval = self.period - (datetime.now().minute % self.period)
			self.mylogger.logger.debug("%s [%s] NEXT SAMPLE IN %d min" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.stock.symbol, nextinterval))			
			time.sleep(60 * nextinterval)
			
	def run_bot(self):
		if self.live:
			self.__livetest()
		else:
			self.__backtest()

	def start_bot(self):
		self.thread.start()

	def stop_bot(self):
		self.thread.join()
