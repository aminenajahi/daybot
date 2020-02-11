from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import ta
import time
import pandas as pd
from datetime import datetime
import math as math

class Broker(object):
    def __init__(self, cash, logger):
        self.budget = cash
        self.cash = cash
        self.invested = 0
        self.profit = 0
        self.perf = 0
        self.mylogger = logger

    def buy_shares(self, stock, nb_shares):
        stock.buy(nb_shares)
        self.cash -= stock.close * nb_shares
        self.invested = stock.avgbuyprice * stock.totalbuysize

    def buy_dollar_amount(self, stock, dollar_amount):
        if self.cash < dollar_amount:
            return

        nb_shares = math.floor(dollar_amount / stock.close)
        self.buy_shares(stock, nb_shares)

    def sell_shares(self, stock, nb_shares):
        nb_shares = math.floor(nb_shares)
        if nb_shares == 0:
            return

        stock.sell(nb_shares)
        self.cash += stock.close * nb_shares
        self.invested = stock.avgbuyprice * stock.totalbuysize

    def print_balance(self, stock):
        self.profit = (self.cash + self.invested) - self.budget
        self.value = stock.totalbuysize * stock.close
        self.perf = self.profit / self.budget * 100
        self.mylogger.logger.debug("[%s] CASH = %8.2f$, INVESTED = %8.2f$, VALUE = %8.2f PROFIT = %8.2f$, PERF = %8.2f%%" % (stock.symbol, self.cash, self.invested, self.value, self.profit, self.perf))