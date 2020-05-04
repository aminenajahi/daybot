# Import the library
from datetime import datetime
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import time
import argparse
from MMBot import MMBot
from BotManager import BotManager
from FinvizScreener import FinvizScreener


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
	ap.add_argument("-i", "--ibk", required=False, help="use interactive broker")
	ap.add_argument("-s", "--since", required=False, help="since")
	ap.add_argument("-g", "--debug", required=False, help="debug")
	ap.add_argument("-f", "--finviz", required=False, help="finviz")
	ap.add_argument("-l", "--liquidate", required=False, help="liquidate")
	ap.add_argument("-o", "--watchlistonly", required=False, help="watchlist only")

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
		period = 5

	if args['backtest']:
		live = False
	else:
		live = True

	if args['email']:
		email = True
	else:
		email = False

	if args['botname']:
		botname = args['botname']
	else:
		botname = 'SimpleBot'

	if args['ibk']:
		ibk = True
	else:
		ibk = False

	if args['since']:
		since = args['since']
	else:
		since = '2019-01-01'

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
		nb_stocks = int(args['finviz'])
		screener = FinvizScreener()
		ticker_pool = []
		gainers = []
		N = 100

		print("=== TOP %d BIGGEST MARKET CAP ===" % N)
		stock_list = screener.top_N_biggest(N)
		for stock in stock_list:
			ticker_pool.append(stock['Ticker'])

		print("=== TOP %d GAINER ===" % nb_stocks)
		stock_list = screener.top_N_gainer(nb_stocks, stock_list=ticker_pool)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		print("=== TOP %d HIGH VOLUME ===" % nb_stocks)
		stock_list = screener.top_N_high_volume(nb_stocks, stock_list=ticker_pool)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		print("=== TOP %d HIGH VOLATILE ===" % nb_stocks)
		stock_list = screener.top_N_volatility(nb_stocks, stock_list=ticker_pool)
		for stock in stock_list:
			watchlist.append(stock['Ticker'])

		#print("=== TOP %d TANKING ===" % nb_stocks)
		#stock_list = screener.top_N_tanking(nb_stocks, stock_list=ticker_pool)
		#for stock in stock_list:
		#	watchlist.append(stock['Ticker'])

		watchlist = list(dict.fromkeys(watchlist))
		print("screener watchlist")
		print(watchlist)

	else:
		finviz = None

	print("CREATE BOT MANAGER %s WITH %d BUDGET" % (botname, budget))
	botManager = BotManager(botname=botname, watchlist=watchlist, budget=budget, quota=quota, period=period, live=live, debug=debug, email=email, daily=daily, ibk=ibk, since=since, liquidate=liquidate, watchlistonly=watchlistonly)

	print("CREATING ALL BOTS")
	botManager.create_bots()

	print("STARTING ALL BOTS")
	botManager.start_bots()

	print("STOPPING ALL BOTS")
	botManager.stop_bot()

	print("BALANCE OF ALL BOTS")
	botManager.printbalance_bot()

	print("TOTAL BOT MANAGER RETURNS")
	botManager.print_total_return()

	time.sleep(5)
	print("END OF PROGRAM")