
import sys
from os.path import dirname
import smtplib
from io import StringIO 
from datetime import datetime
import os
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

sys.path.append('../../')

# Import the library
from FinvizScreener import FinvizScreener

from io import StringIO 
import sys
import logging

def setup_logger(name, log_file, level=logging.DEBUG):
	log_setup = logging.getLogger(name)
	fileHandler = logging.FileHandler(log_file, mode='a+')
	#streamHandler = logging.StreamHandler()
	log_setup.setLevel(level)
	log_setup.addHandler(fileHandler)
	#log_setup.addHandler(streamHandler)
	return log_setup

class Capturing(list):
	def __enter__(self):
		self._stdout = sys.stdout
		sys.stdout = self._stringio = StringIO()
		return self
	def __exit__(self, *args):
		self.extend(self._stringio.getvalue().splitlines())
		del self._stringio    # free up some memory
		sys.stdout = self._stdout

def __notify_user(subject, body, files=None):
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.login("amine.najahi@gmail.com", "bcyamsmgneicstpx")
	msg = "\r\n".join([
		"From: amine.najahi@gmail.com",
		"To: amine.najahi@gmail.com",
		"Subject: %s" % subject,
		"",
		"%s" % body,
		""
	])

	for f in files or []:
		with open(f, "rb") as fi:
			part = MIMEApplication(
				fi.read(),
				Name=basename(f)
			)
			# After the file is closed
			part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
			msg.attach(part)

	server.sendmail("amine.najahi@gmail.com", "amine.najahi@gmail.com", msg)
	server.quit()

if __name__ == '__main__':
	
	logfile = datetime.now().strftime("%d_%m_%Y.log")
	logfile = "scan" + "_" + logfile
	print("CREATING LOGFILE:%s" % logfile)
	
	if os.path.isfile(logfile) == True:
		os.remove(logfile)

	logger = setup_logger("scanner", logfile)

	screener = FinvizScreener(10, logger=logger)

	#with Capturing() as output:
	watchlist = screener.getDailyAlphaFromBigCaps()
	subject = "[MMBOT] SCANNER DAILY UPDATE"
	#body  = ""
	#__notify_user(subject, body, None)