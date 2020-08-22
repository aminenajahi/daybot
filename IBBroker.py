from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import ta
import time
import pandas as pd
from datetime import datetime
import math as math
from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order
import random as random
import uuid
import ezibpy

class IBBroker(object):
    conn = ezibpy.ezIBpy()
    conn.connect(clientId=100, host="localhost", port=4001)
    conn.requestPositionUpdates(subscribe=True)
    conn.requestAccountUpdates(subscribe=True)
    totalbudget = 0
    totalinvested = 0

    def __init__(self, totalbudget, quota, logger):
        IBBroker.totalbudget = totalbudget
        self.quota = quota
        self.cash = quota
        self.invested = 0
        self.profit = 0
        self.perf = 0
        self.mylogger = logger
        self.value = 0
        self.buypending = False
        self.sellpending = False

        print("[IBK] quota %.3f, cash %.3f" % (self.quota, self.cash))

    def buy_short_shares(self, stock, nb_shares, price=None):
        return self.sell_shares(stock, nb_shares, price)

    def sell_short_shares(self, stock, nb_shares, price=None):
        return self.buy_shares(stock, nb_shares, price)

    def buy_shares(self, stock, nb_shares, price=None):
        nb_shares = math.floor(nb_shares)
        if nb_shares == 0:
            return -1

        if IBBroker.totalinvested + nb_shares * stock.close > IBBroker.totalbudget:
            self.mylogger.logger.debug("OVER BUDGET, CANNOT BUY %s" % stock.symbol)
            return -1

        if self.cash < nb_shares * stock.close:
            self.mylogger.logger.debug("NOT ENOUGH CASH LEFT %.3f$ TO BUY %.3f$" % (self.cash, nb_shares * stock.close))
            return -1

        if stock.totalbuysize * stock.avgbuyprice > self.quota:
            self.mylogger.logger.debug("HAVE %.3f$, ABOVE QUOTA OF %.3f$" % (stock.totalbuysize * stock.avgbuyprice, self.quota))
            return -1

        if self.buypending == True and self.buyorder['status'] != "FILLED":
            self.mylogger.logger.debug("BUY ORDER PENDING")
            return -1

        self.buypending = False
        contract = IBBroker.conn.createStockContract(stock.symbol)
        if price is None:
            self.buyorder = IBBroker.conn.createOrder(quantity=nb_shares, rth=True)
        else:
            self.buyorder = IBBroker.conn.createOrder(quantity=nb_shares, price=price, rth=True)
        id = IBBroker.conn.placeOrder(contract, self.buyorder)
        self.mylogger.logger.debug("%s [%s] IBK ORDER ID:%d, BUY %d SHARES @ %.3f$ OF %s" % (datetime.now(), stock.symbol, id, nb_shares,  stock.close, stock.symbol))
        self.mylogger.tradebook.debug("%s [%s] IBK ORDER ID:%d, BUY %d SHARES @ %.3f$ OF %s" % (datetime.now(), stock.symbol, id, nb_shares,  stock.close, stock.symbol))
        time.sleep(5)
        self.buypending = True

        result = stock.buy(nb_shares)
        self.cash -= stock.close * nb_shares
        self.invested = stock.avgbuyprice * stock.totalbuysize
        self.calculate_profit(stock)
        IBBroker.totalinvested += self.invested
        return result

    def sell_shares(self, stock, nb_shares, price=None):
        nb_shares = math.floor(nb_shares)
        if nb_shares == 0:
            return -1

        if self.invested < nb_shares * stock.avgbuyprice:
            return -1

        if self.sellpending == True and self.sellorder['status'] != "FILLED":
            self.mylogger.logger.debug("SELL ORDER PENDING")
            return -1

        self.sellpending = False
        contract = IBBroker.conn.createStockContract(stock.symbol)
        if price is None:
            self.sellorder = IBBroker.conn.createOrder(quantity=nb_shares * -1, rth=True)
        else:
            self.sellorder = IBBroker.conn.createOrder(quantity=nb_shares * -1, price=price, rth=True)
        id = IBBroker.conn.placeOrder(contract, self.sellorder)
        self.mylogger.logger.debug("%s [%s] ORDER ID: %d, SELL %d SHARES @ %.3f$ OF %s" % (datetime.now(), stock.symbol, id, nb_shares, stock.close, stock.symbol))
        self.mylogger.tradebook.debug("%s [%s] ORDER ID: %d, SELL %d SHARES @ %.3f$ OF %s" % (datetime.now(), stock.symbol, id, nb_shares, stock.close, stock.symbol))
        time.sleep(5)
        self.sellpending = True

        result = stock.sell(nb_shares)
        self.cash += stock.close * nb_shares
        self.invested = stock.avgbuyprice * stock.totalbuysize
        self.calculate_profit(stock)
        IBBroker.totalinvested -= self.invested
        return result

    def calculate_profit(self, stock):
        self.profit = (self.cash + self.invested) - self.quota
        self.value = stock.totalbuysize * stock.close
        self.unrzprofit = self.value - self.invested
        self.perf = self.profit / self.quota * 100

    def print_balance(self, stock):
        self.calculate_profit(stock)
        self.mylogger.logger.debug(
            "%s [%6s] #TRANSAC = %d , CASH = %8.2f$, INVESTED = %8.2f$, VALUE = %8.2f RLZ PROFIT = %8.2f$, UNRLZ PROFIT = %8.2f$, PERF = %8.2f%%" % (
            stock.tstamp, stock.symbol, stock.transaction, self.cash, self.invested, self.value, self.profit,
            self.unrzprofit, self.perf))