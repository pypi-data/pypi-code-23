import gzip
import hashlib
import time
from threading import Thread

import ax26.util as util

from ax26 import constants as const


class _Ax26_Handler:
	# New protocol, meant to be the successor to ax25
	def __init__(self, kiss_object, callsign):
		self._k = kiss_object
		self._mycall = callsign.encode()

		self._last_frame = bytearray()
		self._new_frame = False

		# Default variables
		self.max_packet_length = 750
		self.min_packet_length = 15

		self.connection_attempts = 5
		self.send_attempts = 5  # If this fails, connection should probably be dropped
		self.recv_attempts = 5

		self.send_timeout_seconds = 30
		self.receive_timeout_seconds = 30 #Between chunks


		read_thread = Thread(target=self._read_thread)#Start reader thread
		read_thread.daemon = True
		read_thread.start()

	def write(self, from_c, to_c, data):
		self._k.write(util.format_header(from_c, to_c) + data)


	def wait_for_connect(self):
		if self._connected:
			return False
		start_time = time.time()
		while True:
			success, src = self.accept_connection_handler()
			if success:
				self._connected = True
				self._dest_call = src
				return True
			elif time.time() - start_time > 30:  # TODO: Make configureable
				return False

	def accept_connection_handler(self):
		(success, src, dest, type, garbage) = self.get_last_frame(dest_filter=[self._mycall], type_filter=[const.CONNECT])
		if success:
			self._k.write(util.format_header(self._mycall, src) + const.ACK)
			return True, src
		return False, None

	def get_connected_to(self):
		return self._dest_call.decode()

	def get_connection_status(self):
		return self._connected

	def get_last_frame(self, src_filter = None, dest_filter = None, type_filter = None):
		if self._new_frame:
			(src, dest, type_byte, body) = util.decode_packet(self._last_frame)
			if (src_filter is None or src in src_filter) and (dest_filter is None or dest in dest_filter)\
					and (type_filter is None or type_byte in type_filter):
				self._last_frame = bytearray() # Technically Redundant
				self._new_frame = False
				return True, src, dest, type_byte, body
		time.sleep(0.1)  # To keep CPU from pegging at 100% constantly
		return False, None, None, None, None

	def _read_callback(self, frame):
			self._last_frame = frame
			self._new_frame = True

	def _read_thread(self):  # Constantly reads from port, waiting for new data
		self._k.read(callback=self._read_callback)


	def receive_data(self, src_filter=None, dest_filter=None, first_byte=None):
		fulldata = b''
		recvd_packet = False
		recv_from = src_filter
		recv_to = dest_filter

		if first_byte is not None:
			recvd_packet = True
			(chunk, checksum) = first_byte.rsplit(const.CHECKSUM, 1)
			if checksum == hashlib.md5(chunk).hexdigest().encode():
				fulldata += chunk
				self.write(dest_filter[0], src_filter[0], const.ACK)  # Have to be len of 1 if first_byte not None
			else:
				self.write(dest_filter[0], src_filter[0], const.RESEND)

		attempts = 0
		# While DATA_END is not the last packet, or it is, but it's escaped
		while (not fulldata.endswith(const.DATA_END) or fulldata.endswith(const.ESC + const.DATA_END)):
			start_time = time.time()
			while True:  # Keep trying until there's a data chunk. Sometimes there'll be sufficient loopback
				# And the packet sent will be received. This prevents that from interfering.
				(success, src, dest, type_byte, body) = self.get_last_frame(recv_from, recv_to,
																			[const.DATA_CHUNK, const.DATA_START])
				if len(recv_from) > 1:
					recv_from = [src]
				if len(recv_to) > 1:
					recv_to = [dest]
				if success:
					recvd_packet = True  # Start of transmission, so we should say that we've received something
					attempts = 0
					break
				elif not recvd_packet:  # If no packets have been received at all
					return None
				elif time.time() - start_time > self.receive_timeout_seconds:
					attempts += 1
					if attempts > self.recv_attempts:
						return None
					start_time = time.time()
			(chunk, checksum) = body.rsplit(const.CHECKSUM, 1)
			# print(chunk) # DEBUGGING
			if checksum == hashlib.md5(chunk).hexdigest().encode():
				fulldata += chunk
				# print(chunk)  # DEBUGGING
				# Request next
				self.write(recv_to[0], recv_from[0], const.ACK)
			else:
				self.write(recv_to[0], recv_from[0], const.RESEND)

		# print(fulldata) # DEBUGGING
		# print(util.recover_data(fulldata[:-1])) # DEBUGGING
		return gzip.decompress(
			util.recover_data(fulldata[:-1]))  # Decompress. Ignore last byte - It'll be the PAGE_RESPONSE_END delimiter

	def send_data(self, data, src, dest):  # TODO: PACKET IDs

		# 32 for MD5. 3 for byte delimiters
		max_data_chunk_length = self.max_packet_length - (len(src) + len(dest) + 35)

		# print(gzip.compress(data, 9)) # DEBUGGING
		data = util.escape_data(gzip.compress(data, 9)) + const.DATA_END  # Compress data and add DATA_END byte
		# print(data) # DEBUGGING

		attempts = 0
		sep_byte = const.DATA_START
		while data != b'':
			success = True
			start_time = time.time()

			self._k.write(util.format_header(src, dest) + sep_byte +
						data[0:max_data_chunk_length] + const.CHECKSUM +
						  hashlib.md5(data[0:max_data_chunk_length]).hexdigest().encode())
			sep_byte = const.DATA_CHUNK
			# print(html[0:packet_length]) #DEBUGGING
			ack = False  # Wait for client to acknowledge packet, or resend
			while not ack:
				(ack, src_ack, dest_ack, type, garbage) = self.get_last_frame([dest], [src], [const.ACK, const.RESEND])

				if ack:
					if type == const.RESEND:
						success = False
				elif time.time() - start_time > self.send_timeout_seconds:
					success = False
					break

			if success:
				data = data[max_data_chunk_length:]
				attempts = 0
			else:
				attempts += 1

			if attempts >= self.send_attempts:
				self._connected = False
				return False
		return True

