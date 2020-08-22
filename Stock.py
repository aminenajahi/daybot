import math as math
import IBBroker as IBBroker

class Stock(object):

	def __init__(self, symbol, logger, broker):
		self.mylogger = logger
		self.symbol = symbol
		self.tstamp = None
		self.close = 0
		self.totalbuysize = 0
		self.totalinvested = 0
		self.totalvalue = 0
		self.avgbuyprice = 0
		self.profit = 0
		self.profitpercent = 0
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
		self.change = 0
		self.broker=broker
		self.long = 0
		self.short = 0

		try:
			if self.broker.conn.portfolio[symbol]['symbol'] == symbol:
				self.totalbuysize = self.broker.conn.portfolio[symbol]['position']
				self.avgbuyprice = self.broker.conn.portfolio[symbol]['averageCost']
				self.totalinvested = self.broker.conn.portfolio[symbol]['marketValue']

				self.broker.cash = self.broker.quota - (self.totalbuysize * self.avgbuyprice)
				self.broker.invested = self.totalbuysize * self.avgbuyprice
				if self.totalbuysize >= 0:
					self.position = 1

				self.mylogger.logger.debug("LOAD POSITION %s FROM BROKER, HAS %d SHARES @ %.3f$, INVESTED %.3f$, QUOTA %.3f$, CASH LEFT %.3f$" % (symbol, self.totalbuysize, self.avgbuyprice, self.broker.invested, self.broker.quota, self.broker.cash))
			else:
				self.totalbuysize = 0
				self.avgbuyprice = 0
				self.totalinvested = 0

				self.broker.cash = self.broker.quota - (self.totalbuysize * self.avgbuyprice)
				self.broker.invested = self.totalbuysize * self.avgbuyprice
				if self.totalbuysize >= 0:
					self.position = 1
		except:
			print("ERROR UNABLE TO LAOD BROKER POSITIONS")

	def buy(self, nb_shares):
		self.buyprice = self.close
		self.buysize = nb_shares

		self.mylogger.logger.debug(
			"%s [%s] YOU HAVE %.2f SHARES @ AVG PRICE %8.3f$ WORTH %8.3f" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice, (self.totalbuysize * self.avgbuyprice)))
		self.mylogger.logger.debug(
			"%s [%s] WILL BUY %.2f SHARES @ %8.3f$ BUYING FOR %8.3f$" % (self.tstamp, self.symbol, self.buysize, self.close, (self.buysize * self.buyprice)))

		self.totalbuysize += self.buysize
		self.totalinvested += self.buysize * self.buyprice
		self.avgbuyprice = self.totalinvested / self.totalbuysize
		self.mylogger.logger.debug(
			"%s [%s] YOU HAVE %.2f$ SHARES @ AVG PRICE %8.3f$" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice))

		if self.totalbuysize >= 0:
			self.position = 1
			self.long = 1

		return 0

	def buy_short(self, nb_shares):
		self.buyprice = self.close
		self.buysize = nb_shares

		self.mylogger.logger.debug(
			"%s [%s] YOU HAVE SHORT %.2f SHARES @ AVG PRICE %8.3f$ WORTH %8.3f" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice, (self.totalbuysize * self.avgbuyprice)))
		self.mylogger.logger.debug(
			"%s [%s] WILL BUY SHORT %.2f SHARES @ %8.3f$ BUYING FOR %8.3f$" % (self.tstamp, self.symbol, self.buysize, self.close, (self.buysize * self.buyprice)))

		self.totalbuysize += self.buysize
		self.totalinvested += self.buysize * self.buyprice
		self.avgbuyprice = self.totalinvested / self.totalbuysize
		self.mylogger.logger.debug(
			"%s [%s] YOU HAVE SHORT %.2f$ SHARES @ AVG PRICE %8.3f$" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice))

		if self.totalbuysize >= 0:
			self.position = 1
			self.short = 1
	
		return 0

	def sell(self, nb_shares):
		self.sellprice = self.close
		self.sellsize = nb_shares

		self.mylogger.logger.debug(
			"%s [%s] YOU HAVE %.2f SHARES @ AVG %8.3f WORTH %8.3f" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice, (self.totalbuysize * self.avgbuyprice)))
		self.mylogger.logger.debug(
			"%s [%s] WILL SELL %.2f SHARES @ %8.3f WORTH %8.3f" % (self.tstamp, self.symbol, self.sellsize, self.sellprice, (self.sellsize * self.sellprice)))

		self.totalbuysize -= self.sellsize
		self.totalinvested = self.totalbuysize * self.avgbuyprice

		#calculate profit
		self.profitpercent = (self.sellprice - self.avgbuyprice) / self.avgbuyprice * 100
		self.profit = (self.sellprice - self.avgbuyprice) * self.sellsize
		self.totalprofit += self.profit
		self.mylogger.logger.debug("%s [%s] SOLD %.2f SHARES @ %8.3f MADE %.2f%% (%.3f$)" % (
		self.tstamp, self.symbol, self.sellsize, self.sellprice, self.profitpercent, self.profit))

		if self.totalbuysize <= 0:
			self.avgbuyprice = 0
			self.position = 0
			self.long = 0

		self.transaction += 1
		return 0

	def sell_short(self, nb_shares):
		self.sellprice = self.close
		self.sellsize = nb_shares

		self.mylogger.logger.debug(
			"%s [%s] YOU HAVE SHORT %.2f SHARES @ AVG %8.3f WORTH %8.3f" % (self.tstamp, self.symbol, self.totalbuysize, self.avgbuyprice, (self.totalbuysize * self.avgbuyprice)))
		self.mylogger.logger.debug(
			"%s [%s] WILL SELL SHORT %.2f SHARES @ %8.3f WORTH %8.3f" % (self.tstamp, self.symbol, self.sellsize, self.sellprice, (self.sellsize * self.sellprice)))

		self.totalbuysize -= self.sellsize
		self.totalinvested = self.totalbuysize * self.avgbuyprice

		#calculate profit
		self.profitpercent = self.change / self.avgbuyprice * 100
		self.profit = self.change * self.sellsize
		self.totalprofit += self.profit
		self.mylogger.logger.debug("%s [%s] SOLD SHORT %.2f SHARES @ %8.3f MADE %.2f%% (%.3f$)" % (
		self.tstamp, self.symbol, self.sellsize, self.sellprice, self.profitpercent, self.profit))

		if self.totalbuysize <= 0:
			self.avgbuyprice = 0
			self.position = 0
			self.short = 0

		self.transaction += 1
		return 0

	def updatemarketcounter(self, row):

		if self.inmarket != 0 and self.outmarket != 0:
			self.marketratio = self.inmarket / (self.inmarket + self.outmarket) * 100
		else:
			self.marketratio = 0

		if self.position == 1:
			self.inmarket += 1
		else:
			self.outmarket += 1

		try:
			if self.broker.conn.portfolio[self.symbol]['symbol'] == self.symbol:
				self.totalbuysize = self.broker.conn.portfolio[self.symbol]['position']
				self.avgbuyprice= self.broker.conn.portfolio[self.symbol]['averageCost']
				self.totalinvested = self.broker.conn.portfolio[self.symbol]['marketValue']
				#self.broker.cash = self.broker.quota - (self.totalbuysize * self.avgbuyprice)
				self.broker.invested = self.totalbuysize * self.avgbuyprice
				
				if self.avgbuyprice is not 0:
					if self.long == 1:
						self.change = (self.close - self.avgbuyprice) / self.avgbuyprice * 100
					elif self.short == 1:
						self.change = (self.close - self.avgbuyprice) / self.avgbuyprice * 100 * -1
				else:
					self.change = 0

				self.mylogger.logger.debug("long :%d, short:%d change:%8.3f" % (self.long, self.short, self.change))

				if self.totalbuysize > 0:
					self.position = 1
					self.long = 1

			self.mylogger.logger.debug("long :%d, short:%d change:%8.3f position:%d" % (self.long, self.short, self.change, self.position))
	
		except:
			#self.broker.cash = self.broker.quota - (self.totalbuysize * self.avgbuyprice)
			self.broker.invested = self.totalbuysize * self.avgbuyprice
			if self.avgbuyprice is not 0:
				if self.long == 1:
					self.change = (self.close - self.avgbuyprice) / self.avgbuyprice * 100
				elif self.short == 1:
					self.change = (self.close - self.avgbuyprice) / self.avgbuyprice * 100 * -1
			else:
				self.change = 0
	
			if self.totalbuysize > 0:
				self.position = 1
				self.long = 1

		self.mylogger.logger.debug("long :%d, short:%d change:%8.3f position:%d" % (self.long, self.short, self.change, self.position))

		row['inmarket'] = self.inmarket
		row['outmarket'] = self.outmarket
		row['marketratio'] = self.marketratio
		row['totalbuysize'] = self.totalbuysize
		row['avgbuyprice'] = self.avgbuyprice
		row['totalinvested'] = self.totalinvested
		row['brokerinvested'] = self.broker.invested
		row['change'] = self.change
		row['inposition'] = self.position

	
	