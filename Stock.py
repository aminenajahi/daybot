
class Stock(object):

	def __init__(self, symbol, logger):
		self.mylogger = logger
		self.symbol = symbol
		self.tstamp = None
		self.close = 0
		self.buyprice = 0
		self.sellprice = 0
		self.buysize = 0
		self.sellsize = 0
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

	def buy(self, riskfactor, cash):
		self.buyprice = self.close
		self.buysize = cash * riskfactor / self.buyprice
		self.mylogger.logger.debug(
			"%s [%s] HAVE %.2f SHARES @ AVG %8.3f" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice))
		self.mylogger.logger.debug("\n%s [%s] BUY %.2f SHARES @ %8.3f" % (self.tstamp, self.symbol, self.buysize, self.close))

		self.totalbuysize += self.buysize
		self.totalinvested += self.buysize * self.buyprice
		self.avgbuyprice = self.totalinvested / self.totalbuysize
		self.mylogger.logger.debug(
			"%s [%s] HAVE %.2f SHARES @ AVG %8.3f" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice))

		self.position = 1

	def sell(self):
		self.sellprice = self.close
		self.sellsize = self.totalbuysize
		self.mylogger.logger.debug(
			"%s [%s] HAVE %.2f SHARES @ AVG %8.3f" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice))
		self.mylogger.logger.debug("\n%s [%s] SELL %.2f SHARES @ %8.3f" % (self.tstamp, self.symbol, self.sellsize, self.sellprice))

		self.totalbuysize = 0
		self.totalinvested = 0
		self.profit = (self.sellprice - self.avgbuyprice) * self.sellsize
		self.totalprofit += self.profit
		self.mylogger.logger.debug("%s [%s] SOLD %.2f SHARES @ %8.3f MADE %.3f$" % (
		self.tstamp, self.symbol, self.sellsize, self.sellprice, self.profit))

		self.position = 0
		self.transaction += 1

	def updatemarketcounter(self):

		if self.position == 1:
			self.inmarket += 1
		else:
			self.outmarket += 1

