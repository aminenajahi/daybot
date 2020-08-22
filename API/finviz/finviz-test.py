
import sys
from os.path import dirname
import smtplib

sys.path.append('../../')

# Import the library
from FinvizScreener import FinvizScreener

def __notify_user(subject, body):
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
		server.sendmail("amine.najahi@gmail.com", "amine.najahi@gmail.com", msg)
		server.quit()

if __name__ == '__main__':
	screener = FinvizScreener(10)
	#watchlist = screener.getDailyAlphaFromBigCaps()
	watchlist = screener.getCrossingSMA()
	print(watchlist)
	#subject = "[MMBOT] SCANNER DAILY UPDATE"
	#body  = ' '.join([str(elem) for elem in watchlist])
	#__notify_user(subject, body)