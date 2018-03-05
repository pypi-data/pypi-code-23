##
## This module should be compatible across Python 2 and 3
##
## Copyright (C) 2018 Codestruct
## All Rights Reserved.
##
from __future__ import print_function
import socket
import os
import json
import struct
import sys
import select
import errno
import ssl
import random
import time

if sys.version_info.major == 2:
	from Queue import Queue
else:
	from queue import Queue

""" In the API connector, we force the user to supply the API key
def get_api_key():
	path = "%s/.config/cse-node/service-key" % os.environ["HOME"]
	if not os.path.exists(path):
		raise OSError("no service key found at %s" % path)
	data = str()
	with open(path) as f:
		data = f.read().rstrip().replace('\0', '')
	return data
"""

class APISocket:
	def __init__(self):
		self.host = None
		self.port = None
		self.socket = None

		self.write_queue = Queue()

		self.m_on_open = lambda svc: print("%s connected" % str(svc))
		self.m_on_read = lambda x: print("%s" % x)
		self.m_on_close = lambda svc: print("%s closed" % str(svc))

		self.authenticated = False

		self.is_running = False

		self.cb_queue = Queue()
		self.callbacks = dict()

	def on_open(self, f):
		self.m_on_open = f

	def on_read(self, f):
		self.m_on_read = f

	def on_close(self, f):
		self.m_on_close = f

	def run_forever(self):
		self.is_running = True

		self.socket._sock.setblocking(0)
		while self.is_running:
			r, w, e = select.select([self.socket], [self.socket], [], 1.0)
			for fd in r:
				data = self.recv()
				if data:
					data = json.loads(data)
					if "status" in data and data["status"] == True:
						message_id = data["id"]
						cb = self.cb_queue.get()
						self.callbacks[message_id] = cb
					elif "id" in data and data["id"] in self.callbacks:
						self.callbacks[data["id"]](data)
						del self.callbacks[data["id"]]
					else:
						self.m_on_read(data)

			for fd in w:
				if not self.write_queue.empty():
					item = self.write_queue.get()
					self.send(item)

			# Help the CPU out a bit..
			time.sleep(0.02)

	def recv(self):
			size = self.socket.recv(4)
			if not size:
				return None
			if len(size) != 4:
				print("bugged size: %d" % len(size))
			size, = struct.unpack('<I', size)
			tmp = self.socket.recv(size)
			data = tmp
			got = len(data)
			# This needs debugging i i think
			while got < size:
				tmp = self.socket.recv(size - got)
				data += tmp
				got += len(tmp)
			return data

	def send(self, data):
		self.socket.send(struct.pack("I%ds" % len(data), len(data), data.encode("UTF-8")))

	def send_event(self, event):
		data = json.dumps({
			"type": "event",
			"event": event
		})
		self.send(data)

	def send_method(self, method, data=None, callback=None):
		out_data = json.dumps({
			"type": "method",
			"method": method,
			"data": data
		})

		if callback:
			self.cb_queue.put(callback)
		else:
			self.cb_queue.put(self.m_on_read)

		self.send(out_data)

	def connect(self, key, host, port):
		self.host = host
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		self.socket = ssl.wrap_socket(self.socket)
		self.socket.context.load_default_certs()
		self.socket.connect((host, port))

		self.authenticated = self.auth_exchange(key)
		if self.authenticated:
			print("successfully authenticated with cluster server")
			self.m_on_open(self)
			return True

		return False

	def auth_exchange(self, api_key):
		out_data = json.dumps({
			"auth": "api",
			"key": api_key
		})

		out_struct = struct.pack("I%ds" % len(out_data), len(out_data), out_data.encode("UTF-8")) 
		self.socket.send(out_struct)

		size, = struct.unpack("I", self.socket.recv(4))
		response = self.socket.recv(size)
		in_data = json.loads(response)
		print(in_data)
		return in_data["response"] == "auth" and in_data["status"] == True

class API:
	def __init__(self, key, host, port=6666):
		self.api_key = key
		self.api_host = host
		self.api_port = port
		self.api_socket = APISocket()
		self.method_callbacks = dict()

	def send_event(self, event):
		self.api_socket.send_event(event)

	# params should be a list of parameters to supply to the given method
	def send_method(self, method, data=None, callback=None):
		return self.api_socket.send_method(method, data, callback)

	def call_method(self, method, data=None):
		self.api_socket.send_method(method, data)
		data = self.api_socket.recv()
		data = json.loads(data)

		if "error" in data:
			return data

		print("Sent message ID: %s" % str(data["id"]))
		call_data = self.api_socket.recv()
		call_data = json.loads(call_data)

		del call_data["node_id"]
		del call_data["socket_id"]
		return call_data

	def on_read(self, data):
		data = json.loads(data)
		sys.stdout.write(" %d" % data["data"])
		sys.stdout.flush()

	def connect(self):
		self.api_socket.on_read(self.on_read)
		self.api_socket.connect(self.api_key, self.api_host, self.api_port)

	def run_forever(self):
		self.api_socket.run_forever()

if __name__ == "__main__":
	args = sys.argv[1:]
	if len(args) == 0:
		print("usage: %s <api-key>" % sys.argv[0])
		exit(1)

	api = API(args[0], "localhost", 6666)
	api.connect()
	api.send_method("sum", [1, 1], lambda x: print(x["data"] * 2))

	api.run_forever()
