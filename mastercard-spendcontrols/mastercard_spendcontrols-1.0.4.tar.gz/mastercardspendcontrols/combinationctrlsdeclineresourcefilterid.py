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
from mastercardspendcontrols import ResourceConfig

class CombinationctrlsdeclineresourcefilterId(BaseObject):
	"""
	
	"""

	__config = {
		
		"413e7000-a4ed-4cce-aa7a-e14b62fe60c8" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/filters/{filterId}", "delete", [], []),
		
		"e6ea0155-c8df-4935-9175-5cf457c3f701" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/filters/{filterId}", "read", [], []),
		
		"11fc6c96-7ba9-43a0-b84c-75126cbc309b" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/filters/{filterId}", "create", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())





	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type CombinationctrlsdeclineresourcefilterId by id

		@param str id
		@return CombinationctrlsdeclineresourcefilterId of the response of the deleted instance.
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

		return BaseObject.execute("413e7000-a4ed-4cce-aa7a-e14b62fe60c8", CombinationctrlsdeclineresourcefilterId(mapObj))

	def delete(self):
		"""
		Delete object of type CombinationctrlsdeclineresourcefilterId

		@return CombinationctrlsdeclineresourcefilterId of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("413e7000-a4ed-4cce-aa7a-e14b62fe60c8", self)







	@classmethod
	def read(cls,id,criteria=None):
		"""
		Returns objects of type CombinationctrlsdeclineresourcefilterId by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of CombinationctrlsdeclineresourcefilterId
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

		return BaseObject.execute("e6ea0155-c8df-4935-9175-5cf457c3f701", CombinationctrlsdeclineresourcefilterId(mapObj))


	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type CombinationctrlsdeclineresourcefilterId

		@param Dict mapObj, containing the required parameters to create a new object
		@return CombinationctrlsdeclineresourcefilterId of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("11fc6c96-7ba9-43a0-b84c-75126cbc309b", CombinationctrlsdeclineresourcefilterId(mapObj))







