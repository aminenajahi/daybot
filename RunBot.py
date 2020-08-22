# Import the library
from datetime import datetime
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import time
import signal
import argparse
from MMBot import MMBot
from BotManager import BotManager
from FinvizScreener import FinvizScreener
from Broker import Broker

if __name__ == '__main__':
	bots = []

	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_columns', None)
	pd.set_option('display.width', 1000)
	register_matplotlib_converters()

	ap = argparse.ArgumentParser()
	ap.add_argument("-b", "--budget", required=False, help="allocated budget")
	ap.add_argument("-q", "--quota", required=False, help="quota per stock")
	ap.add_argument("-w", "--watchlist", required=False, help="symbols to trade")
	ap.add_argument("-p", "--period", required=False, help="time interval in min 1, 5, 15, 60")
	ap.add_argument("-d", "--daily", required=False, help="use daily market data")
	ap.add_argument("-t", "--backtest", required=False, help="backtest")
	ap.add_argument("-e", "--email", required=False, help="email")
	ap.add_argument("-n", "--botname", required=False, help="botname")
	ap.add_argument("-k", "--brokertype", required=False, help="brokertype to use sim or ibkr")
	ap.add_argument("-s", "--since", required=False, help="since")
	ap.add_argument("-g", "--debug", required=False, help="debug")
	ap.add_argument("-f", "--finviz", required=False, help="finviz")
	ap.add_argument("-l", "--liquidate", required=False, help="liquidate")
	ap.add_argument("-o", "--watchlistonly", required=False, help="watchlist only")
	ap.add_argument("-m", "--marketdata", required=False, help="market data to use sim or ibkr")
	ap.add_argument("-z", "--plot", required=False, help="plot graphs")
	ap.add_argument("-r", "--rth", required=False, help="use outside trading hours")
	ap.add_argument("-x", "--maxbots", required=False, help="maximum number of bots to run")

	args = vars(ap.parse_args())

	if args['budget']:
		budget = int(args['budget'])
	else:
		budget = 5000

	if args['quota']:
		quota = int(args['quota'])
	else:
		quota = 2000

	if args['watchlist']:
		watchlist = args['watchlist'].split(",")
	else:
		watchlist = []

	if args['daily']:
		daily = True
	else:
		daily = False

	if args['period']:
		period = args['period']
	else:
		period = 30

	if args['backtest']:
		live = False
	else:
		live = True

	if args['email']:
		email = True
	else:
		email = False

	if args['rth']:
		rth = False
	else:
		rth = True

	if args['botname']:
		botname = args['botname']
	else:
		botname = 'SimpleBot'

	if args['brokertype']:
		brokertype = args['brokertype']
	else:
		brokertype = "sim"

	if args['marketdata']:
		marketdata = args['marketdata']
	else:
		marketdata = "alpha"

	if args['since']:
		since = args['since']
	else:
		since = '2020-01-01'

	if args['debug']:
		debug = True
	else:
		debug = False

	if args['liquidate']:
		liquidate = True
	else:
		liquidate = False

	if args['watchlistonly']:
		watchlistonly = True
	else:
		watchlistonly = False

	if args['finviz']:
		print("Using Finviz screener")
		nb_stocks = int(args['finviz'])
		screener = FinvizScreener(nb_stocks)
	else:
		screener = False

	if args['maxbots']:
		maxbots = int(args['maxbots'])
	else:
		maxbots = 15

	if args['plot']:
		plot = True
	else:
		plot = False

	print("CREATE BOT MANAGER %s WITH %d BROKET BUDGET" % (botname, budget))
	botManager = BotManager(botname=botname, watchlist=watchlist, budget=budget, quota=quota, period=period, live=live, debug=debug, email=email, daily=daily, brokertype=brokertype, since=since, marketdata=marketdata, screener=screener, liquidate=liquidate, watchlistonly=watchlistonly, rth=rth, maxbots=maxbots)

	print("CREATING ALL BOTS...")
	botManager.create_bots()

	print("STARTING ALL BOTS")
	botManager.start_bots()

	print("STOPPING ALL BOTS")
	botManager.stop_bot()

	print("BOT RESULTS")
	botManager.print_bot_balance()
	
	print("TOTAL BROKER")
	Broker.print_total()

	if plot is True:
		print("PLOT DATA")
		botManager.plot_bot()

	time.sleep(5)
	print("END OF PROGRAM")