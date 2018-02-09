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


from mastercardapicore import BaseObject
from mastercardapicore import RequestMap
from mastercardapicore import OperationConfig
from mastercardapicore import OperationMetadata
from resourceconfig import ResourceConfig

class Retrievals(BaseObject):
	"""
	
	"""

	__config = {
		
		"358ce296-d2ed-42b3-bcb9-13879bb2ce0f" : OperationConfig("/mastercom/v1/claims/{claim-id}/retrievalrequests/{request-id}/fulfillments", "create", [], []),
		
		"8c72741e-c098-4694-be11-f00ecef60b58" : OperationConfig("/mastercom/v1/claims/{claim-id}/retrievalrequests", "create", [], []),
		
		"f36e6551-af69-4a83-9aaf-9b79e3f78a65" : OperationConfig("/mastercom/v1/claims/{claim-id}/retrievalrequests/loaddataforretrievalrequests", "query", [], []),
		
		"b8c10155-9487-4b21-a9e5-cddfe3ed4d2c" : OperationConfig("/mastercom/v1/claims/{claim-id}/retrievalrequests/{request-id}/documents", "query", [], ["format"]),
		
		"f8f8e250-d651-45ba-8ccc-ed26b8ad67da" : OperationConfig("/mastercom/v1/claims/{claim-id}/retrievalrequests/{request-id}/fulfillments/response", "create", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative())


	@classmethod
	def acquirerFulfillARequest(cls,mapObj):
		"""
		Creates object of type Retrievals

		@param Dict mapObj, containing the required parameters to create a new object
		@return Retrievals of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("358ce296-d2ed-42b3-bcb9-13879bb2ce0f", Retrievals(mapObj))






	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Retrievals

		@param Dict mapObj, containing the required parameters to create a new object
		@return Retrievals of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("8c72741e-c098-4694-be11-f00ecef60b58", Retrievals(mapObj))











	@classmethod
	def getPossibleValueListsForCreate(cls,criteria):
		"""
		Query objects of type Retrievals by id and optional criteria
		@param type criteria
		@return Retrievals object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("f36e6551-af69-4a83-9aaf-9b79e3f78a65", Retrievals(criteria))






	@classmethod
	def getDocumentation(cls,criteria):
		"""
		Query objects of type Retrievals by id and optional criteria
		@param type criteria
		@return Retrievals object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("b8c10155-9487-4b21-a9e5-cddfe3ed4d2c", Retrievals(criteria))

	@classmethod
	def issuerRespondToFulfillment(cls,mapObj):
		"""
		Creates object of type Retrievals

		@param Dict mapObj, containing the required parameters to create a new object
		@return Retrievals of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("f8f8e250-d651-45ba-8ccc-ed26b8ad67da", Retrievals(mapObj))







