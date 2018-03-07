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
from mastercardstpapisdk import ResourceConfig

class Supplier(BaseObject):
	"""
	
	"""

	__config = {
		
		"ed5f2920-68d5-4910-81e7-54c9376029cf" : OperationConfig("/stp-api/v1/suppliers/{id}", "read", [], []),
		
		"a85dc977-b0cf-4752-9bfd-4c581a12c582" : OperationConfig("/stp-api/v1/suppliers/{id}", "update", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())






	@classmethod
	def read(cls,id,criteria=None):
		"""
		Returns objects of type Supplier by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Supplier
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

		return BaseObject.execute("ed5f2920-68d5-4910-81e7-54c9376029cf", Supplier(mapObj))



	def update(self):
		"""
		Updates an object of type Supplier

		@return Supplier object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("a85dc977-b0cf-4752-9bfd-4c581a12c582", self)






