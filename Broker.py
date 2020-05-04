from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import ta
import time
import pandas as pd
from datetime import datetime
import math as math

class Broker(object):
    totalbudget = 0
    totalinvested = 0
    totalcash = 0

    def __init__(self, totalbudget, quota, logger):
        Broker.totalbudget = totalbudget
        Broker.totalcash = totalbudget
        self.quota = quota
        self.cash = quota
        self.invested = 0
        self.profit = 0
        self.perf = 0
        self.mylogger = logger
        self.value = 0

    def buy_shares(self, stock, nb_shares):

        self.mylogger.logger.debug("%s [%s] BROKER TOTAL BUDGET %.3f$, CASH %.3f$, QUOTA %.3f$, INVESTED %.3f$" % (stock.tstamp, stock.symbol, Broker.totalbudget, Broker.totalcash, self.quota, Broker.totalinvested))
        stock.buy(nb_shares)
        self.cash -= stock.close * nb_shares
        self.invested = stock.avgbuyprice * stock.totalbuysize
        Broker.totalinvested += stock.close * nb_shares
        Broker.totalcash -= stock.close * nb_shares
        self.calculate_profit(stock)

        return 0

    def sell_shares(self, stock, nb_shares):

        self.mylogger.logger.debug("%s [%s] BROKER TOTAL BUDGET %.3f, CASH %.3f, INVESTED %.3f" % (stock.tstamp, stock.symbol, Broker.totalbudget, Broker.totalcash, Broker.totalinvested))
        stock.sell(nb_shares)
        self.cash += stock.close * nb_shares
        self.invested = stock.avgbuyprice * stock.totalbuysize
        Broker.totalinvested -= stock.close * nb_shares
        Broker.totalcash += stock.close * nb_shares
        self.profit += (self.cash + self.invested) - self.quota
        self.calculate_profit(stock)

        return 0

    def calculate_profit(self, stock):
        self.value = stock.totalbuysize * stock.close
        self.unrzprofit = self.value - self.invested
        self.perf = self.profit / self.quota * 100

        if self.invested != 0:
            self.unrlzperf = self.unrzprofit / self.invested * 100
        else:
            self.unrlzperf = 0


    def print_balance(self, stock):
        self.calculate_profit(stock)
        self.mylogger.logger.debug("%s [%s] #TRANSAC = %d , BUDGET = %8.2f$, INVESTED = %8.2f$, VALUE = %8.2f RLZ PROFIT = %8.2f$, UNRLZ PROFIT = %8.2f$, RLZ PERF = %8.2f%%, UNRLZ PERF =%8.2f%%" % (stock.tstamp, stock.symbol, stock.transaction, self.cash, self.invested, self.value, self.profit, self.unrzprofit, self.perf, self.unrlzperf))