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

class BotManager(object):

	def __init__(self, botname, watchlist, budget, quota, period, live, debug, since, email=False, daily=False, ibk=False, liquidate=False, watchlistonly=False):
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
		self.ibk = ibk
		self.since = since
		self.liquidate = liquidate
		self.watchlistonly = watchlistonly

	def create_mmbot(self, symbol):
		print("LOAD BOT %s FOR %s WITH %d$ QUOTA" % (self.botname, symbol, self.quota))
		mylogger = MyLogger(symbol)

		if self.ibk == False:
			# use simulation broker
			broker = Broker(self.budget, self.quota, mylogger)
		else:
			#use IBK broker
			broker = IBBroker(self.budget, self.quota, mylogger)

		# create and add bot to list of bots
		self.bots.append(
			MMBot(budget=self.quota, symbol=symbol, period=self.period, live=self.live,
				  debug=self.debug,
				  email=self.email, daily=self.daily, broker=broker, mylogger=mylogger, since=self.since,
				  liquidate=self.liquidate))

	def create_bots(self):
		#load existing position from IBK
		if self.ibk == True and self.watchlistonly is False:
			print("LOAD BOTS FROM EXISTING BROKER POSITIONS")
			for symbol in IBBroker.conn.portfolio:
				if symbol not in self.watchlist:
					if self.botname == "MMBot":
						self.create_mmbot(symbol)

		print("CREATE BOTS FROM WATCHLIST")
		for symbol in self.watchlist:
			if self.botname == "MMBot":
				self.create_mmbot(symbol)

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

	def printbalance_bot(self):
		for bot in self.bots:
			bot.print_balance()
			time.sleep(3)

	def print_total_return(self):
		totalbudget = 0
		totalinvested = 0
		totalpotvalue = 0
		totalpotprofit = 0
		totalperf = 0
		totalrlzprofit = 0
		totalrealperf = 0
		totalunrzperf = 0
		totalvalue = 0
		totalunrzprofit = 0
		for bot in self.bots:
			totalrlzprofit += bot.stock.profit
			totalunrzprofit += bot.broker.unrzprofit
			totalvalue += bot.broker.value
			totalinvested += bot.broker.invested

		totalbudget = bot.broker.totalbudget
		totalcash = bot.broker.totalcash

		if totalcash != 0:
			totalrealperf = totalrlzprofit / totalcash * 100
		else:
			totalrealperf = 0

		if totalinvested != 0:
			totalunrzperf = totalunrzprofit / totalinvested * 100
		else:
			totalunrzperf = 0

		print(
			"===TOTAL BUDGET %.2f, CASH %8.2f, TOTAL RLZ PROFIT %8.2f, TOTAL REAL PERF %8.2f%%, TOTAL INVESTED %8.2f, TOTAL VALUE %8.2f, TOTAL UNRZ PROFIT %8.2f$, TOTAL UNRZ PERF %8.2f%%===" % (
			totalbudget, totalcash, totalrlzprofit, totalrealperf,totalinvested,totalvalue,totalunrzprofit,totalunrzperf))
