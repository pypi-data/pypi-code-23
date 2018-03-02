from __future__ import print_function
import time
import hashlib

class tinyblock:

	#Once generate a tinyblock object, a tiny blockchain will be defined.
	#A tiny blockchain has the structure: list[tinyblock1, tinyblock2, ...]
	#A tiny block has the structure: dict{'previous_hash'(str): '..', 'timestamp'(int): '..', 'data'(any): '..', 'nonce'(int): '..', 'next_hash'(str): '..'}

	def __init__(self, chain=[]):
		self.__chain = chain
		assert (type(self.__chain) is list), 'The previous chain must be a list'
		self.__preFormat()

	#Pre-format the input chain.
	def __preFormat(self):
		length = len(self.__chain)
		for i in range(0, length):
			self.__chain[i]['previous_hash'] = str(self.__chain[i]['previous_hash'])
			self.__chain[i]['timestamp'] = int(self.__chain[i]['previous_hash'])
			self.__chain[i]['nonce'] = int(self.__chain[i]['previous_hash'])
			self.__chain[i]['next_hash'] = str(self.__chain[i]['previous_hash'])

	#Add block to the chain.
	#Data is a must. Could set the previous hash of the block.
	def add(self, data, previous_hash='000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'):
		if self.__chain != []:
			previous_hash = self.__chain[-1]['next_hash']
		timestamp = int(time.time())
		next_hash, nonce = self.__getHash(previous_hash, timestamp, data)
		self.__chain += [{'previous_hash': previous_hash, 'timestamp': timestamp, 'data': data, 'nonce': nonce, 'next_hash': next_hash}]

	#Find the blocks with features below. The return elements will content the index in origin chain list.
	#Completely match: previous_hash, nonce, next_hash.
	#Partly match: data. (Currently support str, int, float, list, dict, bool and tuple)
	#Range match: timestamp.(Could be an int, list or tuple)
	def find(self, previous_hash=None, timestamp=None, data=None, nonce=None, next_hash=None):
		blocks = []
		found_flag = 5 - [previous_hash, timestamp, data, nonce, next_hash].count(None)
		index = 0
		assert((timestamp == None) or (type(timestamp) is int) or ((type(timestamp) in [list, tuple]) and (len(timestamp) == 2) \
			and (type(timestamp[0] is int)) and (type(timestamp[1] is int)))), 'The timestamp must be an integer value or a list/tuple contains two integers.'
		for block in self.__chain:
			flag = 0

			if previous_hash != None:
				if block['previous_hash'] == previous_hash:
					flag += 1
			if timestamp != None:
				if type(timestamp) is int:
					if block['timestamp'] == timestamp:
						flag += 1
				if type(timestamp) in [list, tuple]:
					if block['timestamp'] >= timestamp[0] and block['timestamp'] <= timestamp[1]:
						flag += 1
			if data != None:
				if self.__dataFind(data, block['data']):
					flag += 1
			if nonce != None:
				nonce = int(nonce)
				if block['nonce'] == nonce:
					flag += 1
			if next_hash != None:
				if block['next_hash'] == next_hash:
					flag += 1

			if flag == found_flag:
				block['index'] = index
				blocks += [block]
			index += 1
		return blocks

	#Pop the last block from the chain and return this block.
	def pop(self):
		return self.__chain.pop()

	def __dataFind(self, data_part, data):
		data_type = [str, int, float, list, dict, bool, tuple]
		assert((type(data) in data_type) and (type(data_part) in data_type)), 'The find option for data only supports types of str, int, float, list, dict, bool and tuple.'
		if str(data_part) in str(data):
			return True
		return False

	def __getHash(self, previous_hash, timestamp, data):
		nonce = 1
		while True:
			temp_hash = hashlib.sha256((str(nonce) + previous_hash + str(timestamp) + str(data)).encode('utf-8')).hexdigest()
			if self.mineRule(temp_hash):
				return (temp_hash, nonce)
			nonce += 1

	def chainCheck(self, print_option=False):
		index = 0
		for temp in self.__chain:
			if not self.mineRule(temp['previous_hash']):
				if print_option:
					print('The block no.{} has a wrong with previous hash.'.format(index))
				return False
			if index > 0 and temp['previous_hash'] != self.__chain[index-1]['next_hash']:
				if print_option:
					print('The block no.{} has a different previous hash as the previous block.'.format(index))
				return False
			if temp['next_hash'] != self.__getHash(temp['previous_hash'], temp['timestamp'], temp['data'])[0]:
				if print_option:
					print('The block no.{} has a wrong with next hash.'.format(index))
				return False
			index += 1
		return True

	def chainFix(self, start=0, stop=None):
		if stop == None:
			stop = len(self.__chain)
		assert ((start >= 0) and (stop <= len(self.__chain)) and (start <= stop)), 'The start and/or stop point is wrong.'
		assert (self.mineRule(self.__chain[start]['previous_hash'])), 'The first block for fix has a illegal previous hash.'
		for i in range(start, stop):
			if i > start:
				self.__chain[i]['previous_hash'] == self.__chain[i-1]['next_hash']
			self.__chain[i]['next_hash'] = self.__getHash(self.__chain[i]['previous_hash'], self.__chain[i]['timestamp'], self.__chain[i]['data'])

	#Could be override
	def mineRule(self, hash):
		if hash[0:4] == '0000':
			return True
		return False

	#Return chain list
	def getChain(self):
		return self.__chain
