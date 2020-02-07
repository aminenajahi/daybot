# Import the library
from datetime import datetime
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import time
import argparse
from MMBot import MMBot
from SimpleBot import SimpleBot
from BotManager import BotManager

if __name__ == '__main__':
	bots = []

	pd.set_option('display.max_rows', None)
	pd.set_option('display.max_columns', None)
	pd.set_option('display.width', 1000)
	register_matplotlib_converters()

	ap = argparse.ArgumentParser()
	ap.add_argument("-k", "--key", required=False, help="api key")
	ap.add_argument("-b", "--budget", required=False, help="allocated budget")
	ap.add_argument("-w", "--watchlist", required=False, help="symbols to trade")
	ap.add_argument("-p", "--period", required=False, help="time interval in min 1, 5, 15, 60")
	ap.add_argument("-d", "--daily", required=False, help="use daily market data")
	ap.add_argument("-t", "--backtest", required=False, help="backtest")
	ap.add_argument("-e", "--email", required=False, help="email")
	ap.add_argument("-n", "--botname", required=False, help="botname")
	args = vars(ap.parse_args())

	if args['key']:
		apikey = args['key']
	else:
		apikey = 'LCN3E4TILGN8BPA7'

	if args['budget']:
		budget = int(args['budget'])
	else:
		budget = 1000

	if args['watchlist']:
		watchlist = args['watchlist'].split(",")
	else:
		watchlist = ['AAPL', 'MSFT', 'AMZN', 'GOOG', 'TSLA']

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

	totalbudget = len(watchlist) * budget
	print("CREATE BOT MANAGER %s" % botname)
	botManager = BotManager(botname=botname, watchlist=watchlist, key='LCN3E4TILGN8BPA7', budget=totalbudget, period=period, live=live, debug=False, email=email, daily=daily)

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