import math as math

class Stock(object):

	def __init__(self, symbol, logger):
		self.mylogger = logger
		self.symbol = symbol
		self.tstamp = None
		self.close = 0
		self.totalbuysize = 0
		self.totalinvested = 0
		self.totalvalue = 0
		self.avgbuyprice = 0
		self.profit = 0
		self.totalprofit = 0
		self.position = 0
		self.transaction = 0
		self.inmarket = 0
		self.outmarket = 0
		self.marketratio = 0
		self.perf = 0
		self.sellprice = 0
		self.sellsize = 0
		self.buyprice = 0
		self.buysize = 0

	def buy(self, nb_shares):
		self.buyprice = self.close
		self.buysize = nb_shares

		self.mylogger.logger.debug(
			"%s [%s] HAVE %.2f SHARES @ AVG %8.3f" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice))
		self.mylogger.logger.debug(
			"%s [%s] BUY %.2f SHARES @ %8.3f INVEST %8.3f" % (self.tstamp, self.symbol, self.buysize, self.close,(self.buysize * self.buyprice)))

		self.totalbuysize += self.buysize
		self.totalinvested += self.buysize * self.buyprice
		self.avgbuyprice = self.totalinvested / self.totalbuysize
		self.mylogger.logger.debug(
			"%s [%s] HAVE %.2f SHARES @ AVG %8.3f" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice))

		if self.totalbuysize >= 0:
			self.position = 1

		return 0

	def sell(self, nb_shares):
		self.sellprice = self.close
		self.sellsize = nb_shares

		self.mylogger.logger.debug(
			"%s [%s] HAVE %.2f SHARES @ AVG %8.3f" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice))
		self.mylogger.logger.debug(
			"%s [%s] SELL %.2f SHARES @ %8.3f WORTH %8.3f" % (self.tstamp, self.symbol, self.sellsize, self.sellprice, (self.sellsize * self.sellprice)))

		self.totalbuysize -= self.sellsize
		self.totalinvested = self.totalbuysize * self.avgbuyprice

		#calculate profit
		percent = (self.sellprice - self.avgbuyprice) / self.avgbuyprice * 100
		self.profit = (self.sellprice - self.avgbuyprice) * self.sellsize
		self.totalprofit += self.profit
		self.mylogger.logger.debug("%s [%s] SOLD %.2f SHARES @ %8.3f MADE %.2f%% (%.3f$)" % (
		self.tstamp, self.symbol, self.sellsize, self.sellprice, percent, self.profit))

		if self.totalbuysize <= 0:
			self.avgbuyprice = 0
			self.position = 0

		self.transaction += 1

	def updatemarketcounter(self):

		if self.inmarket != 0 and self.outmarket != 0:
			self.marketratio = self.inmarket / (self.inmarket + self.outmarket) * 100
		else:
			self.marketratio = 0

		if self.position == 1:
			self.inmarket += 1
		else:
			self.outmarket += 1

