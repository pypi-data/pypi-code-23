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

class Channeldecline(BaseObject):
	"""
	
	"""

	__config = {
		
		"06366d42-e7ab-4b72-a5c9-062981ef75ee" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/channels", "delete", [], []),
		
		"5feb065d-2459-468a-91c4-d0c78df0234b" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/channels", "query", [], []),
		
		"7d31ea0b-b86d-41f3-8d93-4738411f26d3" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/channels", "create", [], []),
		
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
		Delete object of type Channeldecline by id

		@param str id
		@return Channeldecline of the response of the deleted instance.
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

		return BaseObject.execute("06366d42-e7ab-4b72-a5c9-062981ef75ee", Channeldecline(mapObj))

	def delete(self):
		"""
		Delete object of type Channeldecline

		@return Channeldecline of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("06366d42-e7ab-4b72-a5c9-062981ef75ee", self)








	@classmethod
	def query(cls,criteria):
		"""
		Query objects of type Channeldecline by id and optional criteria
		@param type criteria
		@return Channeldecline object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("5feb065d-2459-468a-91c4-d0c78df0234b", Channeldecline(criteria))

	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Channeldecline

		@param Dict mapObj, containing the required parameters to create a new object
		@return Channeldecline of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("7d31ea0b-b86d-41f3-8d93-4738411f26d3", Channeldecline(mapObj))







