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


class IBBroker(object):
    conn = Connection.create(port=4001, clientId=100)
    #conn.register(my_account_handler, 'UpdateAccountValue')
    #conn.register(my_tick_handler, message.tickSize, message.tickPrice)
    conn.connect()

    def __init__(self, cash, logger):
        self.budget = cash
        self.cash = cash
        self.invested = 0
        self.profit = 0
        self.perf = 0
        self.mylogger = logger

    #def my_account_handler( msg):
    #    print(msg)

    #def my_tick_handler(msg):
    #    print(msg)

    def __make_contract(self, symbol, sec_type, exch, prim_exch, curr):
        contract = Contract()
        contract.m_symbol = symbol
        contract.m_secType = sec_type
        contract.m_exchange = exch
        contract.m_primaryExch = prim_exch
        contract.m_currency = curr
        print("Make contract %s, sec_type %s, exch %s, prim_exch %s, curr %s" %(symbol, sec_type, exch, prim_exch, curr))
        return contract

    def __make_order(self, action, quantity, price=None):
        if price is not None:
            order = Order()
            order.m_orderType = 'LMT'
            order.m_totalQuantity = quantity
            order.m_action = action
            order.m_lmtPrice = price

        else:
            order = Order()
            order.m_orderType = 'MKT'
            order.m_totalQuantity = quantity
            order.m_action = action

        print("Order action %s, type %s, qty %s, lmt %8.3f" % (action, order.m_orderType, order.m_totalQuantity, order.m_lmtPrice))
        return order

    def buy_shares(self, stock, nb_shares):
        nb_shares = math.floor(nb_shares)
        if nb_shares == 0:
            return

        id = int(uuid.uuid1().int % 999)
        print("IBK UUID:%d, BUY %d SHARES OF %s" % (id, nb_shares, stock.symbol))
        for i in range(1,5):
            cont = self.__make_contract(stock.symbol, 'STK', 'SMART', 'SMART', 'USD')
            offer = self.__make_order('BUY', nb_shares, stock.close)
            IBBroker.conn.placeOrder(id, cont, offer)
            time.sleep(5)

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

        id = int(uuid.uuid1().int % 999)
        print("IBK ID:%d, SELL %d SHARES OF %s" % (id, nb_shares, stock.symbol))
        for i in range(1, 5):
            cont = self.__make_contract(stock.symbol, 'STK', 'SMART', 'SMART', 'USD')
            offer = self.__make_order('SELL', nb_shares, stock.close)
            IBBroker.conn.placeOrder(id, cont, offer)
            time.sleep(5)

        stock.sell(nb_shares)
        self.cash += stock.close * nb_shares
        self.invested = stock.avgbuyprice * stock.totalbuysize

    def print_balance(self, stock):
        self.profit = (self.cash + self.invested) - self.budget
        self.value = stock.totalbuysize * stock.close
        self.perf = self.profit / self.budget * 100
        self.mylogger.logger.debug("[%s] CASH = %8.2f$, INVESTED = %8.2f$, VALUE = %8.2f PROFIT = %8.2f$, PERF = %8.2f%%" % (stock.symbol, self.cash, self.invested, self.value, self.profit, self.perf))