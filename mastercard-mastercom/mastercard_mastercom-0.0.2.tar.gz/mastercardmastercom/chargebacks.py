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

class Chargebacks(BaseObject):
	"""
	
	"""

	__config = {
		
		"5d9d89a0-202a-438e-a365-f3e612dcbad2" : OperationConfig("/mastercom/v1/claims/{claim-id}/chargebacks", "create", [], []),
		
		"cd17a678-f280-4b0e-aa9f-811374ec7ecc" : OperationConfig("/mastercom/v1/claims/{claim-id}/chargebacks/{chargeback-id}/reversal", "create", [], []),
		
		"2a03bf7d-d0dc-4056-872d-41c51d852d54" : OperationConfig("/mastercom/v1/claims/{claim-id}/chargebacks/{chargeback-id}/documents", "query", [], ["chargeback-type","format"]),
		
		"0da03038-deaa-4fef-96e8-83b1c4e2e4ff" : OperationConfig("/mastercom/v1/claims/{claim-id}/chargebacks/loaddataforchargebacks", "query", [], []),
		
		"7ca5083b-d45c-414e-95bd-f28d092f5ba3" : OperationConfig("/mastercom/v1/claims/{claim-id}/chargebacks/{chargeback-id}", "update", [], []),
		
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
		Creates object of type Chargebacks

		@param Dict mapObj, containing the required parameters to create a new object
		@return Chargebacks of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("5d9d89a0-202a-438e-a365-f3e612dcbad2", Chargebacks(mapObj))






	@classmethod
	def createReversal(cls,mapObj):
		"""
		Creates object of type Chargebacks

		@param Dict mapObj, containing the required parameters to create a new object
		@return Chargebacks of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("cd17a678-f280-4b0e-aa9f-811374ec7ecc", Chargebacks(mapObj))











	@classmethod
	def retrieveDocumentation(cls,criteria):
		"""
		Query objects of type Chargebacks by id and optional criteria
		@param type criteria
		@return Chargebacks object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("2a03bf7d-d0dc-4056-872d-41c51d852d54", Chargebacks(criteria))






	@classmethod
	def getPossibleValueListsForCreate(cls,criteria):
		"""
		Query objects of type Chargebacks by id and optional criteria
		@param type criteria
		@return Chargebacks object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("0da03038-deaa-4fef-96e8-83b1c4e2e4ff", Chargebacks(criteria))


	def update(self):
		"""
		Updates an object of type Chargebacks

		@return Chargebacks object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("7ca5083b-d45c-414e-95bd-f28d092f5ba3", self)






