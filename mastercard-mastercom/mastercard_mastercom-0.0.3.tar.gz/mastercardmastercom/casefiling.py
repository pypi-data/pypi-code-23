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

class CaseFiling(BaseObject):
	"""
	
	"""

	__config = {
		
		"7804811b-1bd5-47fc-b03b-4d84d1d1090d" : OperationConfig("/mastercom/v1/cases", "create", [], []),
		
		"582762d4-dad0-4fcc-8661-72f52b88dcd3" : OperationConfig("/mastercom/v1/cases/{case-id}/documents", "query", [], ["format","memo"]),
		
		"738578fe-196d-4d33-b2ab-1f2fbab8ae45" : OperationConfig("/mastercom/v1/cases/status", "update", [], []),
		
		"7a62cd63-dbcc-474c-8045-421f5ebc3aca" : OperationConfig("/mastercom/v1/cases/{case-id}", "update", [], []),
		
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
		Creates object of type CaseFiling

		@param Dict mapObj, containing the required parameters to create a new object
		@return CaseFiling of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("7804811b-1bd5-47fc-b03b-4d84d1d1090d", CaseFiling(mapObj))











	@classmethod
	def retrieveDocumentation(cls,criteria):
		"""
		Query objects of type CaseFiling by id and optional criteria
		@param type criteria
		@return CaseFiling object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("582762d4-dad0-4fcc-8661-72f52b88dcd3", CaseFiling(criteria))


	def caseFilingStatus(self):
		"""
		Updates an object of type CaseFiling

		@return CaseFiling object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("738578fe-196d-4d33-b2ab-1f2fbab8ae45", self)






	def update(self):
		"""
		Updates an object of type CaseFiling

		@return CaseFiling object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("7a62cd63-dbcc-474c-8045-421f5ebc3aca", self)






