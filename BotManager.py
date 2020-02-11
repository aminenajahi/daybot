# Import the library
from datetime import datetime
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import time
import argparse
from MMBot import MMBot
from SimpleBot import SimpleBot
from Broker import Broker
from MyLogger import MyLogger

class BotManager(object):

	def __init__(self, botname, watchlist, key, budget, period, live, debug, since, email=False, daily=False, ibk=False):
		self.botname = botname
		self.budget = budget
		self.cash = budget
		self.watchlist = watchlist
		self.period = period
		self.daily = daily
		self.live = live
		self.debug = debug
		self.email = email
		self.riskfactor = 1
		self.key = key
		self.bots = []
		self.budget_per_stock = self.budget / len(self.watchlist)
		self.ibk = ibk
		self.since = since

	def run_bot(self):
		self.backtest()

	def create_bots(self):
		for symbol in self.watchlist:
			print("CREATE BOT %s FOR %s WITH %d$" % (self.botname, symbol, self.budget_per_stock))
			if self.botname == "MMBot":
				print("creating mmbot")
				self.bots.append(
					MMBot(key=self.key, budget=self.budget_per_stock, symbol=symbol, period=self.period, live=self.live, debug=self.debug,
						  email=self.email, daily=self.daily, ibk=self.ibk, since=self.since))
			else:
				print("creating simplebot")
				self.bots.append(SimpleBot(key=self.key, budget=self.budget_per_stock, symbol=symbol, period=self.period, live=self.live,
									  debug=self.debug, email=self.email, daily=self.daily))

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
		totalcash = 0
		totalinvested = 0
		totalpotvalue = 0
		totalpotprofit = 0
		totalperf = 0
		totalrealprofit = 0
		totalrealperf = 0
		totalvalue = 0
		for bot in self.bots:
			totalcash += bot.broker.cash
			totalinvested += bot.stock.totalinvested
			totalrealprofit += bot.stock.totalprofit
			totalvalue += bot.broker.value

		totalrealperf = totalrealprofit / self.budget * 100
		print(
			"===TOTAL CASH %8.2f, TOTAL REAL PROFIT %8.2f, TOTAL REAL PERF %8.2f%%, TOTAL INVESTED %8.2f, TOTAL VALUE %8.2f===" % (
			totalcash, totalrealprofit, totalrealperf,totalinvested,totalvalue))
