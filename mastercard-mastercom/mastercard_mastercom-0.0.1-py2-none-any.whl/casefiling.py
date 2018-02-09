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

class CaseFiling(BaseObject):
	"""
	
	"""

	__config = {
		
		"2d9b4ce0-ad71-4d03-9288-87b6c025abea" : OperationConfig("/mastercom/v1/cases", "create", [], []),
		
		"4641e326-42a7-42ac-b0f0-398abf709128" : OperationConfig("/mastercom/v1/cases/{case-id}/documents", "query", [], ["format"]),
		
		"67adfc45-1349-4c33-afd5-413db5741c50" : OperationConfig("/mastercom/v1/cases/{case-id}", "update", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative())


	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type CaseFiling

		@param Dict mapObj, containing the required parameters to create a new object
		@return CaseFiling of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("2d9b4ce0-ad71-4d03-9288-87b6c025abea", CaseFiling(mapObj))











	@classmethod
	def retrieveDocumentation(cls,criteria):
		"""
		Query objects of type CaseFiling by id and optional criteria
		@param type criteria
		@return CaseFiling object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("4641e326-42a7-42ac-b0f0-398abf709128", CaseFiling(criteria))


	def update(self):
		"""
		Updates an object of type CaseFiling

		@return CaseFiling object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("67adfc45-1349-4c33-afd5-413db5741c50", self)






