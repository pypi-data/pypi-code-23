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
import time

if sys.version_info.major == 2:
	from Queue import Queue
else:
	from queue import Queue

def get_service_key():
	path = "%s/.csenet/node/service-key" % os.environ["HOME"]
	if not os.path.exists(path):
		raise OSError("no service key found at %s" % path)
	data = str()
	with open(path) as f:
		data = f.read().rstrip().replace('\0', '')
	return data

class ServiceSocket:
	def __init__(self):
		self.host = None
		self.port = None
		self.socket = None

		self.write_queue = Queue()

		self.m_on_open = lambda svc: print("%s connected" % str(svc))
		self.m_on_read = lambda x: print("on_read: %s" % x)
		self.m_on_close = lambda svc: print("%s closed" % str(svc))

		self.authenticated = False

		self.is_running = False

	def on_open(self, f):
		self.m_on_open = f

	def on_read(self, f):
		self.m_on_read = f

	def on_close(self, f):
		self.m_on_close = f

	def run_forever(self):
		self.is_running = True

		while self.is_running:
			r, w, e = select.select([self.socket], [self.socket], [], 1.0)
			if r == [self.socket]:
				self.socket.setblocking(1)
				size = self.socket.recv(4)
				if size is None or len(size) != 4:
					self.socket.setblocking(0)
					return False

				size, = struct.unpack("<I", size)
				data = self.socket.recv(size)
				self.socket.setblocking(0)

				if not data:
					return False

				self.m_on_read(data)

			if w == [self.socket] and not self.write_queue.empty():
				item = self.write_queue.get()
				self.send(item)

			time.sleep(0.02)

	def stop(self):
		self.is_running = False

	def send(self, data):
		self.socket.send(struct.pack("<I%ds" % len(data), len(data), data.encode("UTF-8")))

	def enqueue(self, data):
		self.write_queue.put(data)

	def connect(self, host, port):
		self.host = host
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		self.socket.connect((host, port))

		## Go SSL
		self.socket = ssl.wrap_socket(self.socket, cert_reqs=ssl.CERT_NONE)

		self.authenticated = self.auth_exchange()
		if self.authenticated:
			print("successfully authenticated with cluster server")
			self.m_on_open(self)
			return True

		return False

	def auth_exchange(self):
		out_data = json.dumps({
			"auth": "service",
			"key": get_service_key()
		})

		print("Using key: %s" % get_service_key())
		print("Using out_data: %s" % str(out_data))
		out_struct = struct.pack("I%ds" % len(out_data), len(out_data), out_data.encode("UTF-8")) 
		self.socket.send(out_struct)

		size, = struct.unpack("I", self.socket.recv(4))
		response = self.socket.recv(size)
		print(response)
		in_data = json.loads(response.decode("UTF-8"))
		print(in_data)
		return in_data["response"] == "auth" and in_data["status"] == True

class Service:
	def __init__(self):
		self.service_socket = ServiceSocket()
		self.event_callbacks = dict()
		self.method_callbacks = dict()

	def provide_method(self, method, callback):
		out_data = json.dumps({
			"type": "method",
			"action": "subscribe",
			"method": method
		})

		self.service_socket.send(out_data)
		self.method_callbacks[method] = callback

	def register_event(self, event, callback):
		out_data = json.dumps({
			"type": "event",
			"action": "subscribe",
			"event": event
		})
		self.event_callbacks[event] = callback
		self.service_socket.send(out_data)

	def on_event(self, data):
		if "key" in data:
			if data["key"] != get_service_key():
				print("%s event registration was given an invalid key" % data["event"])
				return None

			if data["action"] == "subscribe":
				if data["status"] == False:
					event = data["event"]
					del self.event_callbacks[event]
				else:
					print("%s event registered with server" % data["event"])
		else:
			if data["event"] in self.event_callbacks:
				self.event_callbacks[data["event"]](data)

	def on_method(self, data):

		_type = data["type"]
		
		if "action" in data and data["action"] == "subscribe":
			## We expect data["status"] here
			method = data["method"]
			if data["key"] != get_service_key():
				print("%s method registration was given an invalid key" % method)
				return None

			if method in self.method_callbacks:
				print("%s method registered with server" % data["method"])

			print("%s method was successfully subscribed to" % data["method"])
			return True

		print("attached request: %s" % str(data))
		# Unattach ids, user doesnt need them
		socket_id = data["socket_id"]
		del data["socket_id"]

		message_id = data["id"]
		del data["id"]

		node_id = data["node_id"]
		del data["node_id"]
		print("unattached request: %s" % str(data))

		if data["method"] in self.method_callbacks:
			method = data["method"]
			ret = self.method_callbacks[method](data)
			print("method reply: %s" % str(ret))
			# Reattach ids
			ret["id"] = message_id
			ret["node_id"] = node_id
			ret["socket_id"] = socket_id
			print("reattached reply: %s" % str(ret))

			# Add our responded to method data to outgoing queue
			self.service_socket.send(json.dumps(ret))
		else:
			print("%s method called but no method provided" % data["method"])

	def on_read(self, data):
		print("got data: %s" % data)
		data = json.loads(data)
		if data["type"] == "event":
			self.on_event(data)
		elif data["type"] == "method":
			self.on_method(data)

	def on_ping(self, data):
		print("on_ping: called")

	def on_sum(self, data):
		c = 0
		for i in data["data"]:
			c += i
		data["data"] = c
		return data

	def connect(self, host="localhost", port=6667):
		self.service_socket.on_read(self.on_read)
		self.service_socket.connect(host, port)

	def run_forever(self, host="localhost", port=6667, debug=True):
		self.service_socket.run_forever()

if __name__ == "__main__":
	port = 6667
	if len(sys.argv) > 1:
		port = int(sys.argv[1])

	service = Service()
	try:
		service.run_forever(port=port)
	except KeyboardInterrupt:
		pass

