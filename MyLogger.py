from datetime import datetime
import logging

class MyLogger(object):

	def __init__(self, symbol):
		self.logfile = datetime.now().strftime("%d_%m_%Y.log")
		self.logfile = "logs/" + symbol + "_" + self.logfile
		self.logger = self.setup_logger(symbol, self.logfile)

	def setup_logger(self, name, log_file, level=logging.DEBUG):
		log_setup = logging.getLogger(name)
		fileHandler = logging.FileHandler(log_file, mode='a')
		streamHandler = logging.StreamHandler()
		log_setup.setLevel(level)
		log_setup.addHandler(fileHandler)
		log_setup.addHandler(streamHandler)
		return log_setup
