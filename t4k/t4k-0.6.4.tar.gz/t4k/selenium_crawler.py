##!/usr/bin/env python
#
#'''
#This module enables crawling reddit.com to obtain the html representing
#users' profiles.  It is executable and takes one arguments.  To crawl
#users, run `./crawl_users.py users`.
#
#The very first time you run this file, you may need to create a tracker,
#which is a file that the crawler uses to keep track of which users
#have already been crawled.  To do that, run `./crawl_users.py setup`.
#
#The tracker is built from a plain text list of 
#active users, which should be listed, one user per line, inside the file 
#`active-users.txt`.  This file should be stored in DATA_DIR 
#(which is a path specified in the project settings in `SETTINGS.py`).
#'''
#
#
#import time
#from pyvirtualdisplay import Display
#from selenium import webdriver
#from selenium.webdriver.support.ui import WebDriverWait 
#from selenium.webdriver.support.select import Select
#from selenium.common.exceptions import (
#	TimeoutException, NoSuchElementException, WebDriverException, 
#	StaleElementReferenceException
#)
#
#
#def uses_selenium(f):
#	'''
#	This is a decorator, which is intended to be used to decorate methods
#	of the Crawler class (or subclasses), which contain a selenium.webdriver
#	instance as the attribute `driver`.
#
#	Ensures that the webdriver is closed after a the decorated function 
#	completes, or in case an exception occurs within it.
#	'''
#
#	def wrapped(self, *args, **kwargs):
#
#		# If needed, make and start a display
#		if self.use_display:
#			self.display = Display(visible=0, size=(1024, 768))
#			self.display.start()
#
#		# make a selenium webdriver, and a wait
#		self.driver = webdriver.Firefox()
#		self._wait = WebDriverWait(self.driver, self.WAIT_TIME)
#
#		# Run the function in a try block
#		try:
#			return_val = f(self, *args, **kwargs)
#
#		# Quit driver and stop the display in case of exception...
#		except:
#			self.driver.quit()
#			if self.use_display:
#				self.display.stop()
#			raise
#
#		# ...Or after function completes
#		self.driver.quit()
#		if self.use_display:
#			self.display.stop()
#
#		# Return the original return value
#		return return_val
#
#	return wrapped
#
#
#class SeleniumCrawler(object):
#
#	REQUEST_DELAY = 1.2
#	WAIT_TIME = 30
#
#	# These are added to the crawler's namespace for convevenievce
#	# This way they don't need to be imported from Selenium
#	Select = Select
#	TimeoutException = TimeoutException
#	NoSuchElementException = NoSuchElementException
#	WebDriverException = WebDriverException
#	StaleElementReferenceException = StaleElementReferenceException
#
#
#	def __init__(self, use_display=True):
#		self.use_display = use_display
#
#
#	def delay(self):
#		'''
#		Ensures that between any two calls to delay(), at least 
#		self.REQUEST_DELAY seconds will have elapsed.
#		'''
#		if hasattr(self, '_timer'):
#			elapsed = time.time() - self._timer
#			remaining = self.REQUEST_DELAY - elapsed
#			time.sleep(max(0, remaining))
#
#		self._timer = time.time()
#
#
#	def quit_webdriver(self):
#		self.driver.quit()
#
#
#	def get_page_source(self):
#		return self.driver.page_source.encode('utf8')
#
#
#	def wait(self, f, args=(), kwargs={}):
#		return self._wait.until(lambda driver: f(*args, **kwargs))
#
#
#class UnexpectedPageException(Exception):
#	pass
#
#
#
#if __name__ == '__main__':
#	
#	if USE_PYVIRTUALDISPLAY:
#		display = Display(visible=0, size=(1024, 768))
#		display.start()
#
#	# Run the appropriate function.
#	try:
#		dispatch()
#
#	# Afterwards, or if there is an exception, stop the display if needed.
#	except:
#		if USE_PYVIRTUALDISPLAY:
#			display.stop()
#		raise
#	else:
#		if USE_PYVIRTUALDISPLAY:
#			display.stop()
