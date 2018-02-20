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
from mastercardspendalerts import ResourceConfig

class Card(BaseObject):
	"""
	
	"""

	__config = {
		
		"efa2e5f0-bb5c-457a-b048-5ea4a5fb4a08" : OperationConfig("/issuer/v1/card", "create", [], []),
		
		"429fc1c4-1cd4-4d03-a5dc-c451d7d49837" : OperationConfig("/issuer/v1/card/{uuid}", "read", [], []),
		
		"1e0f98e0-621c-4f09-9df2-febdd7722a9b" : OperationConfig("/issuer/v1/card/uuid", "create", [], []),
		
		"03e50c9e-19f3-42e3-b6b4-e2956dc11141" : OperationConfig("/issuer/v1/card/{uuid}", "delete", [], []),
		
		"fa758465-d439-4c9f-8621-ce855113b617" : OperationConfig("/issuer/v1/card/{uuid}", "create", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())


	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Card

		@param Dict mapObj, containing the required parameters to create a new object
		@return Card of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("efa2e5f0-bb5c-457a-b048-5ea4a5fb4a08", Card(mapObj))










	@classmethod
	def retrievePan(cls,id,criteria=None):
		"""
		Returns objects of type Card by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Card
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

		return BaseObject.execute("429fc1c4-1cd4-4d03-a5dc-c451d7d49837", Card(mapObj))


	@classmethod
	def read(cls,mapObj):
		"""
		Creates object of type Card

		@param Dict mapObj, containing the required parameters to create a new object
		@return Card of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("1e0f98e0-621c-4f09-9df2-febdd7722a9b", Card(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type Card by id

		@param str id
		@return Card of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""

		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if map:
			if (isinstance(map,RequestMap)):
				mapObj.setAll(map.getObject())
			else:
				mapObj.setAll(map)

		return BaseObject.execute("03e50c9e-19f3-42e3-b6b4-e2956dc11141", Card(mapObj))

	def delete(self):
		"""
		Delete object of type Card

		@return Card of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("03e50c9e-19f3-42e3-b6b4-e2956dc11141", self)



	@classmethod
	def update(cls,mapObj):
		"""
		Creates object of type Card

		@param Dict mapObj, containing the required parameters to create a new object
		@return Card of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("fa758465-d439-4c9f-8621-ce855113b617", Card(mapObj))







