# Import the library
from datetime import datetime
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import time
import argparse
from MMBot import MMBot
from SimpleBot import SimpleBot

class BotManager(object):

	def __init__(self, botname, watchlist, key, budget, period, live, debug, email = False, daily = False):
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
		self.bots = []
		self.budget_per_stock = self.budget / len(self.watchlist)
		print("Creating botmanager")
	def run_bot(self):
		self.backtest()

	def create_bots(self):
		for symbol in self.watchlist:
			print("CREATE BOT %s FOR %s WITH %d$" % (self.botname, symbol, self.budget_per_stock))
			if self.botname == "MMBot":
				print("creating mmbot")
				self.bots.append(
					MMBot(key='LCN3E4TILGN8BPA7', budget=self.budget_per_stock, symbol=symbol, period=self.period, live=self.live, debug=self.debug,
						  email=self.email, daily=self.daily))
			else:
				print("creating simplebot")
				self.bots.append(SimpleBot(key='LCN3E4TILGN8BPA7', budget=self.budget_per_stock, symbol=symbol, period=self.period, live=self.live,
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
		for bot in self.bots:
			totalcash += bot.cash
			totalinvested += bot.stock.totalinvested
			totalpotvalue += bot.stock.potentialvalue
			totalpotprofit += bot.stock.potentialprofit
			totalrealprofit += bot.stock.totalprofit

		totalperf = totalpotprofit / (totalcash + totalinvested) * 100
		totalrealperf = totalrealprofit / self.budget * 100
		print(
			"===TOTAL CASH %8.2f, TOTAL REAL PROFIT %8.2f, TOTAL REAL PERF %8.2f%%, TOTAL INVESTED %8.2f, TOTAL POT VALUE %8.2f TOTAL POT PROFIT %8.2f, TOTAL POT PERF %8.2f%%===" % (
			totalcash, totalrealprofit, totalrealperf,totalinvested, totalpotvalue, totalpotprofit, totalperf))
