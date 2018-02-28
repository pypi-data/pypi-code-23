#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2016 MasterCard International Incorporated
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of
# conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other materials
# provided with the distribution.
# Neither the name of the MasterCard International Incorporated nor the names of its
# contributors may be used to endorse or promote products derived from this software
# without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


from __future__ import absolute_import
from mastercardapicore import BaseObject
from mastercardapicore import RequestMap
from mastercardapicore import OperationConfig
from mastercardapicore import OperationMetadata
from mastercardmastercom import ResourceConfig

class Retrievals(BaseObject):
	"""
	
	"""

	__config = {
		
		"3b040fbc-0f09-4764-9dd7-163cb94e9154" : OperationConfig("/mastercom/v1/claims/{claim-id}/retrievalrequests/{request-id}/fulfillments", "create", [], []),
		
		"b315ffd3-a7a9-4f21-8025-243e17374625" : OperationConfig("/mastercom/v1/claims/{claim-id}/retrievalrequests", "create", [], []),
		
		"94ebeb5d-98cb-45db-85bf-ce75e58905e7" : OperationConfig("/mastercom/v1/claims/{claim-id}/retrievalrequests/loaddataforretrievalrequests", "query", [], []),
		
		"83430cd4-65ca-4fdd-b1bb-89e92b8fe4b0" : OperationConfig("/mastercom/v1/claims/{claim-id}/retrievalrequests/{request-id}/documents", "query", [], ["format"]),
		
		"6343d39d-edb7-4e66-8739-cc239b3e389b" : OperationConfig("/mastercom/v1/claims/{claim-id}/retrievalrequests/{request-id}/fulfillments/response", "create", [], []),
		
		"6c75cfea-3575-4abb-ae2a-6296094fc54d" : OperationConfig("/mastercom/v1/retrievalrequests/status", "update", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())


	@classmethod
	def acquirerFulfillARequest(cls,mapObj):
		"""
		Creates object of type Retrievals

		@param Dict mapObj, containing the required parameters to create a new object
		@return Retrievals of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("3b040fbc-0f09-4764-9dd7-163cb94e9154", Retrievals(mapObj))






	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Retrievals

		@param Dict mapObj, containing the required parameters to create a new object
		@return Retrievals of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("b315ffd3-a7a9-4f21-8025-243e17374625", Retrievals(mapObj))











	@classmethod
	def getPossibleValueListsForCreate(cls,criteria):
		"""
		Query objects of type Retrievals by id and optional criteria
		@param type criteria
		@return Retrievals object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("94ebeb5d-98cb-45db-85bf-ce75e58905e7", Retrievals(criteria))






	@classmethod
	def getDocumentation(cls,criteria):
		"""
		Query objects of type Retrievals by id and optional criteria
		@param type criteria
		@return Retrievals object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("83430cd4-65ca-4fdd-b1bb-89e92b8fe4b0", Retrievals(criteria))

	@classmethod
	def issuerRespondToFulfillment(cls,mapObj):
		"""
		Creates object of type Retrievals

		@param Dict mapObj, containing the required parameters to create a new object
		@return Retrievals of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("6343d39d-edb7-4e66-8739-cc239b3e389b", Retrievals(mapObj))







	def retrievalFullfilmentStatus(self):
		"""
		Updates an object of type Retrievals

		@return Retrievals object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("6c75cfea-3575-4abb-ae2a-6296094fc54d", self)






