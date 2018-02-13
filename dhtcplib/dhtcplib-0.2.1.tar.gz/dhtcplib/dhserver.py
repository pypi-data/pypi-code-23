'''
The MIT License

Copyright (c) 2010-2017 Josh A. Bosley, http://joshbosley.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import threading
import logging
import socketserver
from .dhtransmitter import outgoingQuery
from .dhhandler import handler as defaultHandler

logging.basicConfig(format='%(asctime)s [TCP LIB]: %(message)s <%(levelname)s>')

class TCPConnectionHandler(socketserver.BaseRequestHandler):

    def handle(self):

        # Retrieve incomming message size
        timeout = 5
        try:
            request_size = self.request.recv(4096) 

        except socket.timeout:
            pass

        # If its not a size, cut the connection
        try:
            request_size = int(request_size)
        except:
            self.request.send("__SIZE_ERROR__".encode())
            self.request.close()
            return -1
        
        self.request.send("__ACCEPTED__".encode())

        # Receive the chunks of data from the client
        chunks = []
        bytes_recd = 0
        while bytes_recd < request_size:
            chunk = self.request.recv(min(request_size - bytes_recd, 2048))
            if chunk == b'':
                self.logger.info("__EMPTY__REQUEST__")
                self.request.send("__EMPTY__REQUEST__".encode())
                self.request.close()
                return -1

            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)

        # Join the input data
        data = (b"".join(chunks))

        # Inform the other end that we have their data
        self.request.send("__ACCEPTED__".encode())

        # Gather the reply
        reply = self.handler.handle(data).encode()

        # Inform the other end the length of the reply
        self.request.send(str(len(reply)).encode() )

        # Get verification that the size is accepted
        try:
            verification = self.request.recv(4096).decode("utf-8")
        except:
            self.logger.warning("__VAILED_TO_VERIFY_REQUEST_SEND")
            return -1

        # Ensure that the verification was accepted
        if verification != "__ACCEPTED__":
            self.logger.info("__VERIFICATION_ERROR__")
            return -1

		# Send the data
        total = 0
        while total < len(reply):
            sent = self.request.send(reply[total:])
            if 0 == sent:
                self.logger.warning("__VAILED_TO_VERIFY_REQUEST_SEND")
            total = total + sent

		# Check to make sure the request was sent
        try:
            verification = self.request.recv(4096).decode("utf-8")
        except:
            self.logger.warning("__CANT_VERIFY_SENT_REQUEST__")
            return -1

        if verification != "__ACCEPTED__":
            self.logger.warning("__SENT_DATA_CANT_BE_VERIFIED__")
            return -1

		# Close transmission
        self.request.close()

class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    
	daemon_threads = True
	allow_reuse_address = True

	def __init__(self, address, RequestHandlerClass, RouterClass):
        # For request handling
		if RouterClass is not None:
			RequestHandlerClass.handler = RouterClass
		else:
			RequestHandlerClass.handler = defaultHandler


		RequestHandlerClass.logger = logging.getLogger(__name__)
		# init server
		socketserver.TCPServer.__init__(self, address, RequestHandlerClass)

	def serve(self):
		self.handle_request()

	def force_stop(self):
		self.signal = False
		self.server_close()
		
class dhtcp(threading.Thread):
	def __init__(self, address, port, RouterClass=None):
		threading.Thread.__init__(self)
		self.signal = True
		self.daemon = True
		self.port = port
		self.address = address
		self.serv = Server( 
                (address,port), TCPConnectionHandler, RouterClass
            )

	def kill(self):
		self.serv.force_stop()
		outgoingQuery(self.port, self.address, "null")
		self.signal = False
			
	def run(self):
		while self.signal:
			self.serv.serve()
		self.serv.force_stop()
			
