#!/usr/bin/env python

'''
Cisco Copyright 2018
Author: Vamsi Kalapala <vakalapa@cisco.com>

FILENAME: AZURESTORAGE.PY


'''
from azure.storage.file import FileService
import json
import logging 

log = logging.getLogger('dmvpn')
log.setLevel(logging.INFO)
'''
https://azure-storage.readthedocs.io/en/latest/ref/azure.storage.file.fileservice.html

'''

class azsto():
	def __init__(self,account_name, account_key):
		self.azure_file_service = FileService(account_name=account_name,account_key=account_key)

	def get_file_contents(self, file_share,folder,file_name):
		is_file = self.azure_file_service.exists(file_share,directory_name=folder,file_name=file_name)
		if is_file:
			filedata = self.azure_file_service.get_file_to_text(file_share,folder,file_name)
			log.info(filedata.content)
			#filedata_json =  json.loads(filedata.content)
			return True, filedata.content
		else:
			return False, None


	def write_file_contents(self, file_share,folder,file_name,file_contents):
		self.azure_file_service.create_share(file_share)
		self.azure_file_service.create_directory(file_share, folder)
		for k,v in file_contents.items():
			file_contents[k] = str(v)
		output = self.azure_file_service.create_file_from_text(file_share, folder, file_name, json.dumps(file_contents))
		return output


	def get_file_contents_json(self, file_share,folder,file_name):
		status, output = self.get_file_contents(file_share,folder,file_name)
		if status:
			return True, json.loads(output)
		else:
			return False, None