import configparser
import logging
import getpass

from authentication.authentication import Authentication
from service.batchService import BatchService
import sys,os
import json

class Batch:
	def __init__(self,baseUrl,userName,password):
		self.baseUrl = baseUrl
		self.ngsUri = '/nexus/ngs'
		self.userName = userName
		self.password = password
		self.config = configparser.RawConfigParser()
		self.package_dir = os.path.dirname(os.path.abspath(__file__))
		#self.readCfg()
		self.login()
		

	def readCfg(self):
		self.config.read(os.path.join(self.package_dir,'init.cfg'))
		self.ngsUri = self.config.get('ngs','base_uri')

	def login(self):
		self.auth = Authentication()
		self.auth.performLogin(self.baseUrl,self.userName,self.password)

	def logOut(self):
		self.auth.performLogOut(self.baseUrl,self.userName)

	def getAll(self):
		batchDashborad = BatchService.getAll(self.baseUrl)
		return batchDashborad

	def get(self,batchId):
		batch = BatchService.get(self.baseUrl,batchId)
		return batch

	def getResultsCardData(self,batchId):
		result = BatchService.getResultsCardData(self.baseUrl,self.ngsUri,batchId)
		return result

	def getTaskReview(self,taskId):
		return BatchService.getTaskReview(self.baseUrl,self.ngsUri,taskId)

	










