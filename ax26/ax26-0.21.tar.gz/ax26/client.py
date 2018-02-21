import time

import ax26.classes as classes

from ax26 import constants as const


class Client:
	def __init__(self, kiss_object, callsign):

		self._mycall = callsign.encode()
		self._dest_call = ''
		self._connected = False

		self._ax26 = classes._Ax26_Handler(kiss_object, callsign)

		self.connection_attempts = 5

	def connect(self, to_call):
		to_call = to_call.encode()
		if self._connected:
			return False
		attempts = 0
		while attempts < self._ax26.connection_attempts:
			self._ax26.write(self._mycall, to_call, const.CONNECT)
			start_time = time.time()
			while True:
				success, src_ack, dest_ack, type, garbage = self._ax26.get_last_frame([to_call], [self._mycall], [const.ACK])
				if success:
					self._connected = True
					self._dest_call = to_call
					return True
				elif time.time() - start_time > 5:  # TODO: Make configurable
					attempts += 1
					break
		return False

	def send_data(self, data):
		if not self._connected:
			return False  # Possibly make this an exception
		return self._ax26.send_data(data, self._mycall, self._dest_call)

	def receive_data(self):
		if not self._connected:
			return False
		return self._ax26.receive_data([self._dest_call], [self._mycall])

	def disconnect(self):
		if not self._connected:
			return False
		attempts = 0
		while attempts < self.connection_attempts:
			self._ax26.write(self._mycall, self._dest_call, const.DISCONNECT)
			start_time = time.time()  # TODO: Make configurable
			while True:
				(success, src_ack, dest_ack, type, garbage) = self._ax26.get_last_frame(dest_filter=[self._mycall],
																				  type_filter=[const.ACK])
				if success:
					self._connected = False
					self._dest_call = b''
					return True
				elif time.time() - start_time > 5:  # TODO: Make configureable
					attempts += 1
					break
		# Disconnect anyway. Should not be forced into an indefinite connection if the peer dies
		self._dest_call = b''
		self._connected = False
		return False