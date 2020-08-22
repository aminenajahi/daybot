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
    totalrlzprofit = 0
    
    def print_total():
        print("TOTAL BUDGET = %.2f$, TOTAL CASH = %.2f$, TOTAL INVESTED = %.2f$, TOTAL RLZPROFIT = %.2f$" % (Broker.totalbudget, Broker.totalcash, Broker.totalinvested, Broker.totalrlzprofit))

    def __init__(self, totalbudget, quota, logger):
        Broker.totalbudget = totalbudget
        Broker.totalcash = totalbudget
        self.quota = quota
        self.cash = quota
        self.profit = 0
        self.profitperf = 0
        self.invested = 0
        self.rlzprofit = 0
        self.unrlzprofit = 0
        self.perf = 0
        self.mylogger = logger
        self.value = 0
        self.transactions = []
        self.tx = pd.DataFrame(columns=['TS', 'ACTION', 'SYMBOL', 'C', 'SHARES', 'AVG COST', 'PROFIT', 'PROFIT %', 'CASH', 'INVESTED', 'VALUE', 'RLZPROFIT', 'UNRLZPROFIT'])
    
    def buy_shares(self, stock, nb_shares):

        self.mylogger.logger.debug("%s [%s] LONG BROKER TOTAL BUDGET %.3f$, CASH %.3f$, QUOTA %.3f$, INVESTED %.3f$" % (stock.tstamp, stock.symbol, Broker.totalbudget, Broker.totalcash, self.quota, Broker.totalinvested))
        stock.buy(nb_shares)
        self.cash -= (stock.close * nb_shares)
        self.invested = (stock.avgbuyprice * stock.totalbuysize)
        self.value = (stock.close * stock.totalbuysize)
        Broker.totalcash -= self.cash
        Broker.totalinvested += self.cash
        self.calculate_profit(stock)
        
        self.tx = self.tx.append({'TS' : stock.tstamp, 'ACTION' : "BUY LONG", 'SYMBOL' : stock.symbol, 'C' : stock.close, 'SHARES' : nb_shares, 'AVG COST' : stock.avgbuyprice, 'PROFIT' : 0, 'PROFIT %' : 0, 'CASH' : self.cash, 'INVESTED' : self.invested, 'VALUE' : self.value, 'RLZPROFIT' : self.rlzprofit, 'UNRLZPROFIT' : self.unrlzprofit}, ignore_index=True)
        return 0


    def buy_short_shares(self, stock, nb_shares):

        self.mylogger.logger.debug("%s [%s] SHORT BROKER TOTAL BUDGET %.3f$, CASH %.3f$, QUOTA %.3f$, INVESTED %.3f$" % (stock.tstamp, stock.symbol, Broker.totalbudget, Broker.totalcash, self.quota, Broker.totalinvested))
        stock.buy_short(nb_shares)
        self.cash -= (stock.close * nb_shares)
        self.invested = (stock.avgbuyprice * stock.totalbuysize)
        self.value = (stock.close * stock.totalbuysize)
        Broker.totalcash -= self.cash
        Broker.totalinvested += self.cash
        self.calculate_profit(stock)
        
        self.tx = self.tx.append({'TS' : stock.tstamp, 'ACTION' : "BUY SHORT", 'SYMBOL' : stock.symbol, 'C' : stock.close, 'SHARES' : nb_shares, 'AVG COST' : stock.avgbuyprice, 'PROFIT' : 0, 'PROFIT %' : 0, 'CASH' : self.cash, 'INVESTED' : self.invested, 'VALUE' : self.value, 'RLZPROFIT' : self.rlzprofit, 'UNRLZPROFIT' : self.unrlzprofit}, ignore_index=True)
        return 0

    def sell_shares(self, stock, nb_shares):

        self.mylogger.logger.debug("%s [%s] LONG BROKER TOTAL BUDGET %.3f, CASH %.3f, INVESTED %.3f" % (stock.tstamp, stock.symbol, Broker.totalbudget, Broker.totalcash, Broker.totalinvested))
        self.profit = (stock.close - stock.avgbuyprice) * nb_shares
        self.profitperf = self.profit / (stock.avgbuyprice * stock.totalbuysize) * 100
        self.rlzprofit += self.profit

        stock.sell(nb_shares)
        self.cash += (stock.close * nb_shares)
        self.invested = (stock.avgbuyprice * stock.totalbuysize)        
    
        Broker.totalcash += self.cash 
        Broker.totalinvested -= self.cash       
        Broker.totalrlzprofit += self.rlzprofit
        self.calculate_profit(stock)

        self.tx = self.tx.append({'TS' : stock.tstamp, 'ACTION' : "SELL LONG", 'SYMBOL' : stock.symbol, 'C' : stock.close, 'SHARES' : nb_shares, 'AVG COST' : stock.avgbuyprice, 'PROFIT' : self.profit, 'PROFIT %' : self.profitperf, 'CASH' : self.cash, 'INVESTED' : self.invested, 'VALUE' : self.value, 'RLZPROFIT' : self.rlzprofit, 'UNRLZPROFIT' : self.unrlzprofit}, ignore_index=True)

        return 0

    def sell_short_shares(self, stock, nb_shares):

        self.mylogger.logger.debug("%s [%s] SHORT BROKER TOTAL BUDGET %.3f, CASH %.3f, INVESTED %.3f" % (stock.tstamp, stock.symbol, Broker.totalbudget, Broker.totalcash, Broker.totalinvested))
        self.profit = stock.change * nb_shares
        self.profitperf = self.profit / (stock.avgbuyprice * stock.totalbuysize) * 100
        self.rlzprofit += self.profit

        stock.sell_short(nb_shares)
        self.cash += (stock.close * nb_shares)
        self.invested = (stock.avgbuyprice * stock.totalbuysize)        
    
        Broker.totalcash += self.cash 
        Broker.totalinvested -= self.cash       
        Broker.totalrlzprofit += self.rlzprofit
        self.calculate_profit(stock)

        self.tx = self.tx.append({'TS' : stock.tstamp, 'ACTION' : "SELL SHORT", 'SYMBOL' : stock.symbol, 'C' : stock.close, 'SHARES' : nb_shares, 'AVG COST' : stock.avgbuyprice, 'PROFIT' : self.profit, 'PROFIT %' : self.profitperf, 'CASH' : self.cash, 'INVESTED' : self.invested, 'VALUE' : self.value, 'RLZPROFIT' : self.rlzprofit, 'UNRLZPROFIT' : self.unrlzprofit}, ignore_index=True)

        return 0

    def calculate_profit(self, stock):
        self.value = stock.totalbuysize * stock.close
        self.unrlzprofit = self.value - self.invested
        self.perf = self.rlzprofit / self.quota * 100

        if self.invested != 0:
            self.unrlzperf = self.unrlzprofit / self.invested * 100
        else:
            self.unrlzperf = 0

    def print_transactions(self, stock):
        self.mylogger.tradebook.debug(self.tx)


    def print_balance(self, stock):
        self.calculate_profit(stock)
        self.mylogger.logger.debug("%s [%s]  #TRANSAC = %d , BUDGET = %8.2f$, INVESTED = %8.2f$, VALUE = %8.2f RLZ PROFIT = %8.2f$, UNRLZ PROFIT = %8.2f$, RLZ PERF = %8.2f%%, UNRLZ PERF =%8.2f%%" % (stock.tstamp, stock.symbol, stock.transaction, self.cash, self.invested, self.value, self.rlzprofit, self.unrlzprofit, self.perf, self.unrlzperf))