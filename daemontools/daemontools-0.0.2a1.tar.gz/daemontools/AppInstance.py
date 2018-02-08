#!/usr/bin/env python

'''
Module for previous instance detection.
Author: Lubos Medovarsky, lubos@medovarsky.com, 2008
Copyright: LGPLv3
'''
from __future__ import print_function
import os.path
import time

#class used to handle one application instance mechanism
class ApplicationInstance:

	#specify the file used to save the application instance pid
	def __init__(self, pid_file):
		self.pid_file = pid_file
		self.check()

	#check if the current application is already running
	def check(self):
		#check if the pidfile exists
		if not os.path.isfile(self.pid_file):
			return

		#read the pid from the file
		pid = 0
		try:
			fd = open(self.pid_file, 'rt')
			data = fd.read()
			fd.close()
			pid = int(data)
		except:
			pass

		#check if the process with specified by pid exists
		if 0 == pid:
			return

		try: #flock(pidfile)?
			os.kill(pid, 0)	#this will raise an exception if the pid is not valid
		except:
			return

		#exit the application
		print("The application is already running !")
		exit(0) #exit raise an exception so don't put it in a try/except block
		#return True

	#called when the single instance starts to save it's pid
	def startApplication(self):
		fh = open(self.pid_file, 'wt')
		fh.write(str(os.getpid()))
		fh.close()

	#called when the single instance exit ( remove pid file )
	def exitApplication(self):
		try:
			os.remove(self.pid_file)
		except:
			pass

if __name__ == '__main__':
	#create application instance
	appInstance = ApplicationInstance( '/var/lock/AppInstance.pid' )
	#do something here
	print("Test only: pretending as running for a moment...")
	time.sleep(10)
	#remove pid file
	appInstance.exitApplication()

