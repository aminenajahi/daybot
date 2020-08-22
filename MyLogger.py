from datetime import datetime
import os
import logging

class MyLogger(object):

	intialized = False

	def __init__(self, symbol, live):
		if live:
			folder="livetests"
		else:
			folder="backtests"

		self.logfile = datetime.now().strftime("%d_%m_%Y.log")
		self.logfile = "logs/" + folder + "/" + symbol + "_" + self.logfile
		print("CREATING LOGFILE:%s" % self.logfile)

		self.tradefile = datetime.now().strftime("%d_%m_%Y.log")
		self.tradefile = "trades/" + folder + "/" + self.tradefile
		print("CREATING TRADE BOOK FILE:%s" % self.tradefile)
		
		if MyLogger.intialized == False:
			if live == False:
				if os.path.isfile(self.logfile) == True:
					os.remove(self.logfile)

				if os.path.isfile(self.tradefile) == True:
					os.remove(self.tradefile)
		
		MyLogger.intialized = True
		self.logger = self.setup_logger(symbol, self.logfile)
		self.tradebook = self.setup_logger("tradebook", self.tradefile)

	def setup_logger(self, name, log_file, level=logging.DEBUG):
		log_setup = logging.getLogger(name)
		fileHandler = logging.FileHandler(log_file, mode='a+')
		#streamHandler = logging.StreamHandler()
		log_setup.setLevel(level)
		log_setup.addHandler(fileHandler)
		#log_setup.addHandler(streamHandler)
		return log_setup
