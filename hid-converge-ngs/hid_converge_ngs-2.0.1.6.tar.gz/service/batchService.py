import logging
import json

from authentication.gateway import GateWayService
import xml.etree.ElementTree as et
import urllib
import re
from service import RelationshipEnum
from service.DictionaryEntry import DictionaryEntry
from QueueModule.q import flushableQ


class BatchService:
	def __init__():
		pass

	@staticmethod
	def getAll(baseUrl):
		url = baseUrl+'/platform/common/searchEngine/search?language=en_US'
		payload = json.dumps({"fetchContext":"com.lifetech.converge.domain.Batch",
			                  "filterContext":"com.lifetech.converge.domain.Batch",
			                  "attributes":["uid"],
			                  "operands":["NOT NULL"],
			                  "values":[None],
			                  "dataTypeArray":["String"],
			                  "filterCriteria":[],
			                  "fetchAttributes":["id","uid","externalUid","name","status","taskType.name","description","operator.userName","startedTime","completedTime","method.name","createdTime","updatedTime"]})
		return GateWayService.callConverge(url, 'true', payload)

	@staticmethod
	def get(baseUrl,batchId):
		url = baseUrl+'/platform/common/searchEngine/search?language=en_US'
		payload = json.dumps({"fetchContext":"com.lifetech.converge.domain.Batch",
			                  "filterContext":"com.lifetech.converge.domain.Batch",
			                  "attributes":["uid"],
			                  "operands":["="],
			                  "values":[batchId],
			                  "dataTypeArray":["String"],
			                  "filterCriteria":[],
			                  "fetchAttributes":["id","uid","externalUid","name","status","taskType.name","description","operator.userName","startedTime","completedTime","method.name","createdTime","updatedTime"]})
		return GateWayService.callConverge(url, 'true', payload)


	@staticmethod
	def getResultsCardData(baseUrl,ngsUri,batchId):
		batch = BatchService.get(baseUrl,batchId)[0]
		if batch:
			url = baseUrl+ngsUri+'/batch/getResultsCardData/'+str(batch['id'])+'?language=en_US'
			payload = {}
			return GateWayService.callConverge(url, 'false', payload)
		else:
			return []

	@staticmethod
	def getTaskReview(baseUrl,ngsUri,taskId):
		url = baseUrl+ngsUri+'/task/review/'+str(taskId)+'/STR?language=en_US'
		payload = {}
		return GateWayService.callConverge(url, 'false', payload)








