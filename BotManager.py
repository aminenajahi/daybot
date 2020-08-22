# Import the library
from datetime import datetime
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import time
import argparse
from MMBot import MMBot
from Broker import Broker
from IBBroker import IBBroker
from MyLogger import MyLogger
from Market import Market
from IBMarket import IBMarket

class BotManager(object):

	def __init__(self, botname, watchlist, budget, quota, period, live, debug, since, marketdata, screener=False, email=False, daily=False, brokertype=False, liquidate=False, watchlistonly=False, rth=False, maxbots=False):
		self.botname = botname
		self.budget = budget
		self.cash = budget
		self.watchlist = watchlist
		self.period = period
		self.daily = daily
		self.live = live
		self.debug = debug
		self.email = email
		self.bots = []
		self.quota = quota
		self.brokertype = brokertype
		self.since = since
		self.liquidate = liquidate
		self.watchlistonly = watchlistonly
		self.marketdata = marketdata
		self.screener = screener
		self.rth = rth
		self.maxbots = maxbots

	def create_mmbot(self, symbol):
		print("CREATE MMBOT %s FOR %s WITH %d$ QUOTA TO RUN LIVE:%d" % (self.botname, symbol, self.quota, self.live))
		mylogger = MyLogger(symbol, self.live)

		if self.brokertype == "ibkr":
			print("CREATE IBKR BROKER")
			broker = IBBroker(self.budget, self.quota, mylogger)
		else:
			print("CREATE SIM MARKET")
			broker = Broker(self.budget, self.quota, mylogger)

		if self.marketdata == "ibkr":
			print("CREATE IBKR MARKET DATA")
			market = IBMarket(self.rth)
		else:
			print("CREATE ALPHA VANTAGE MARKER DATA")
			market = Market()	

		# create and add bot to list of bots
		self.bots.append(
			MMBot(budget=self.quota, symbol=symbol, period=self.period, live=self.live,
				  debug=self.debug,
				  email=self.email, daily=self.daily, broker=broker,  market=market, mylogger=mylogger, since=self.since,
				  liquidate=self.liquidate))

	def create_bots(self):
		# load posisiton from watchlist only
		if self.watchlistonly is not False:
			print("WATCHLIST ONLY %s" % self.watchlistonly)
		else:
			if self.screener is not False:
				print(self.screener)
				#screenerlist = self.screener.getDailyAlphaFromBigCaps()
				screenerlist = self.screener.getCrossingSMA()
				print("LOAD SYMBOLS FROM SCREENER")
				print(screenerlist)
				for symbol in screenerlist:
					self.watchlist.append(symbol)
			
			if self.brokertype == "ibkr":
				print("LOAD SYMBOLS FROM EXISTING BROKER POSITIONS")
				print(IBBroker.conn.positions)
				for symbol in IBBroker.conn.positions:
					self.watchlist.append(symbol)
		
		unique_list = []
		for symbol in self.watchlist:
			if symbol not in unique_list:
				print(symbol)
				unique_list.append(symbol)
		
		if self.maxbots != False:
			print("TRIM BOTS TO %d FIRST ONES" % self.maxbots)
			unique_list = unique_list[:self.maxbots]

		print("LOAD BOTS FROM UNIQUE WATCHLIST")
		print(unique_list)
		for symbol in unique_list:
			if self.botname == "MMBot":
				self.create_mmbot(symbol)


	def run_bots(self):
		for bot in self.bots:
			print("RUN BOT FOR %s" % bot.symbol)
			bot.run_bot()
			time.sleep(3)

	def start_bots(self):
		for bot in self.bots:
			print("START BOT FOR %s" % bot.symbol)
			bot.start_bot()
			time.sleep(3)

	def stop_bot(self):
		for bot in self.bots:
			print("WAIT BOT FOR %s" % bot.symbol)
			bot.stop_bot()
			time.sleep(3)

	def print_bot_balance(self):
		for bot in self.bots:
			print("TRADES FOR BOT %s" % bot.symbol)
			bot.print_balance()
			print("===============================")
	
	def plot_bot(self):
		for bot in self.bots:
			bot.plot_data()