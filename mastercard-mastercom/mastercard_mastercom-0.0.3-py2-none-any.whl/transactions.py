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

class Transactions(BaseObject):
	"""
	
	"""

	__config = {
		
		"9bb45b1b-7a9a-4c4b-aca3-2b17cd7fa029" : OperationConfig("/mastercom/v1/claims/{claim-id}/transactions/clearing/{transaction-id}", "read", [], []),
		
		"96fe83d3-c0cc-46ae-bc16-a22d0e7dd952" : OperationConfig("/mastercom/v1/claims/{claim-id}/transactions/authorization/{transaction-id}", "read", [], []),
		
		"b7e305de-ae2c-405c-868e-709d5ad8bb04" : OperationConfig("/mastercom/v1/transactions/search", "create", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())






	@classmethod
	def retrieveClearingDetail(cls,id,criteria=None):
		"""
		Returns objects of type Transactions by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Transactions
		@raise ApiException: raised an exception from the response status
		"""
		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if criteria:
			if (isinstance(criteria,RequestMap)):
				mapObj.setAll(criteria.getObject())
			else:
				mapObj.setAll(criteria)

		return BaseObject.execute("9bb45b1b-7a9a-4c4b-aca3-2b17cd7fa029", Transactions(mapObj))






	@classmethod
	def retrieveAuthorizationDetail(cls,id,criteria=None):
		"""
		Returns objects of type Transactions by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Transactions
		@raise ApiException: raised an exception from the response status
		"""
		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if criteria:
			if (isinstance(criteria,RequestMap)):
				mapObj.setAll(criteria.getObject())
			else:
				mapObj.setAll(criteria)

		return BaseObject.execute("96fe83d3-c0cc-46ae-bc16-a22d0e7dd952", Transactions(mapObj))


	@classmethod
	def searchForTransaction(cls,mapObj):
		"""
		Creates object of type Transactions

		@param Dict mapObj, containing the required parameters to create a new object
		@return Transactions of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("b7e305de-ae2c-405c-868e-709d5ad8bb04", Transactions(mapObj))







