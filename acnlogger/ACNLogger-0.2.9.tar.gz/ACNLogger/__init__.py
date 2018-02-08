#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class ACNLogger:

	def debug(self, session, message):
		try:
			self.logger.debug(("["+session+"]  ["+self._service_name+"]  [DEBUG]  "+str(message)).encode('utf8'))
		except:
			try:
				self.logger.debug("["+session+"]  ["+self._service_name+"]  [DEBUG]  "+str(message))
			except:
				self.logger.debug(("["+session+"]  ["+self._service_name+"]  [DEBUG]  "+str(message)).decode('utf8'))

	def info(self, session, message):
		try:
			self.logger.info(("["+session+"]  ["+self._service_name+"]  [INFO]  "+str(message)).encode('utf8'))
		except:
			try:
				self.logger.info("["+session+"]  ["+self._service_name+"]  [INFO]  "+str(message))
			except:
				self.logger.info(("["+session+"]  ["+self._service_name+"]  [INFO]  "+str(message)).decode('utf8'))

	def warning(self, session, message):
		try:
			self.logger.warning(("["+session+"]  ["+self._service_name+"]  [WARNING]  "+str(message)).encode('utf8'))
		except:
			try:
				self.logger.warning("["+session+"]  ["+self._service_name+"]  [WARNING]  "+str(message))
			except:
				self.logger.warning(("["+session+"]  ["+self._service_name+"]  [WARNING]  "+str(message)).decode('utf8'))

	def error(self, session, e):
		try:
			self.logger.error(("["+session+"]  ["+self._service_name+"]  [ERROR]  "+str(e.__class__.__name__)+"  "+str(e.message)).encode('utf8'))
		except:
			try:
				self.logger.error("["+session+"]  ["+self._service_name+"]  [ERROR]  "+str(e.__class__.__name__)+"  "+str(e.message))
			except:
				self.logger.error(("["+session+"]  ["+self._service_name+"]  [ERROR]  "+str(e.__class__.__name__)+"  "+str(e.message)).decode('utf8'))

	def critical(self, session, e):
		try:
			self.logger.critical(("["+session+"]  ["+self._service_name+"]  [CRITICAL]  "+str(e.__class__.__name__)+"  "+str(e.message)).encode('utf8'))
		except:
			try:
				self.logger.critical("["+session+"]  ["+self._service_name+"]  [CRITICAL]  "+str(e.__class__.__name__)+"  "+str(e.message))
			except:
				self.logger.critical(("["+session+"]  ["+self._service_name+"]  [CRITICAL]  "+str(e.__class__.__name__)+"  "+str(e.message)).decode('utf8'))

	def exception(self, session, e):
		try:
			self.logger.error(("["+session+"]  ["+self._service_name+"]  [ERROR]  "+str(e.__class__.__name__)+"  "+str(e.message)).encode('utf8'))
		except:
			try:
				self.logger.error("["+session+"]  ["+self._service_name+"]  [ERROR]  "+str(e.__class__.__name__)+"  "+str(e.message))
			except:
				self.logger.error(("["+session+"]  ["+self._service_name+"]  [ERROR]  "+str(e.__class__.__name__)+"  "+str(e.message)).decode('utf8'))



	def __init__(self,name,file):

		logging.basicConfig(format=u'[%(asctime)s]  %(message)s', level=logging.DEBUG)

		BC_logger=logging.getLogger(name) # Creating the new logger
		BC_logger.setLevel(logging.DEBUG) # Setting new logger level to INFO or above

		file_handler=logging.FileHandler(file) #Creating handler for log file
		file_handler.setLevel(logging.INFO) 

		BC_logger.addHandler(file_handler) #Adding file handler to the new logger

		formatter=logging.Formatter(u'[%(asctime)s]  %(message)s') #Creating a formatter

		file_handler.setFormatter(formatter) #Setting handler format

		self.logger=BC_logger
		self._service_name=name

		self.info("UNDEFINED","STARTING MICROSERVICE")
