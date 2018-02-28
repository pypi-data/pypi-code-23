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

class Chargebacks(BaseObject):
	"""
	
	"""

	__config = {
		
		"ce3fd3ca-cb0f-43c6-b40b-f853a01f46b4" : OperationConfig("/mastercom/v1/chargebacks/acknowledge", "update", [], []),
		
		"947eadd1-ed95-48bf-982f-87a18f1cb0be" : OperationConfig("/mastercom/v1/claims/{claim-id}/chargebacks", "create", [], []),
		
		"f7a58e9b-a5f8-4441-84ce-d8f0261f10fb" : OperationConfig("/mastercom/v1/claims/{claim-id}/chargebacks/{chargeback-id}/reversal", "create", [], []),
		
		"baaf4e7f-988c-4f28-af2c-28ed45847ad1" : OperationConfig("/mastercom/v1/claims/{claim-id}/chargebacks/{chargeback-id}/documents", "query", [], ["format"]),
		
		"9d036686-7ac9-48ba-9c7a-98654e70f20f" : OperationConfig("/mastercom/v1/claims/{claim-id}/chargebacks/loaddataforchargebacks", "query", [], []),
		
		"e70eded4-6967-48a7-8baa-fdaa4c944a3e" : OperationConfig("/mastercom/v1/chargebacks/status", "update", [], []),
		
		"d00cd102-fa5b-4550-8b0c-2df1f911d788" : OperationConfig("/mastercom/v1/claims/{claim-id}/chargebacks/{chargeback-id}", "update", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())



	def acknowledgeReceivedChargebacks(self):
		"""
		Updates an object of type Chargebacks

		@return Chargebacks object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("ce3fd3ca-cb0f-43c6-b40b-f853a01f46b4", self)





	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Chargebacks

		@param Dict mapObj, containing the required parameters to create a new object
		@return Chargebacks of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("947eadd1-ed95-48bf-982f-87a18f1cb0be", Chargebacks(mapObj))






	@classmethod
	def createReversal(cls,mapObj):
		"""
		Creates object of type Chargebacks

		@param Dict mapObj, containing the required parameters to create a new object
		@return Chargebacks of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("f7a58e9b-a5f8-4441-84ce-d8f0261f10fb", Chargebacks(mapObj))











	@classmethod
	def retrieveDocumentation(cls,criteria):
		"""
		Query objects of type Chargebacks by id and optional criteria
		@param type criteria
		@return Chargebacks object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("baaf4e7f-988c-4f28-af2c-28ed45847ad1", Chargebacks(criteria))






	@classmethod
	def getPossibleValueListsForCreate(cls,criteria):
		"""
		Query objects of type Chargebacks by id and optional criteria
		@param type criteria
		@return Chargebacks object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("9d036686-7ac9-48ba-9c7a-98654e70f20f", Chargebacks(criteria))


	def chargebacksStatus(self):
		"""
		Updates an object of type Chargebacks

		@return Chargebacks object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("e70eded4-6967-48a7-8baa-fdaa4c944a3e", self)






	def update(self):
		"""
		Updates an object of type Chargebacks

		@return Chargebacks object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("d00cd102-fa5b-4550-8b0c-2df1f911d788", self)






