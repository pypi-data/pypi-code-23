import logging
import threading
from sys import getsizeof
from xmlrpc.server import SimpleXMLRPCServer

'''
    Network Memory
    A network-attatched memory module. For a module to be reached
    by external systems, ip must be set to the current device ip
    instead of the loopback address 
'''
class netmem(threading.Thread):
    def __init__(self, auth_token, port, host=None, max_storage=None):
        # Init thread
        threading.Thread.__init__(self)

        # Check variables and setup self
        try:
            if max_storage is not None:
                self.max_storage = int(max_storage)
            else:
                self.max_storage = None
            self.port = int(port)
            self.auth_token = str(auth_token)
        except ValueError as _err:
            logging.error(_err)
            raise
        if self.port < 1 or self.port > 65535:
            logging.error("Port number out of range")
            raise Exception("Invalid port")

        # Memory information
        # This will be a dict of dicts
        self.memory = {}
        self.lock = threading.Lock()

        self.errors = {
            "AUTH": "INVALID_AUTH_TOKEN",
            "CAP": "MEMORY_CAP_REACHED",
            "KEY": "MEMORY KEY NOT FOUND",
            "OKAY": "SUCCESS"
        }

        if host is None:
            self.host = "localhost"
        else:
            self.host = host

        # Create the XMLRPC server
        self.server = SimpleXMLRPCServer(
            (self.host, self.port), 
            logRequests=True
            )

        # Register Memory functions
        self.server.register_function(self.memory_put)
        self.server.register_function(self.memory_fetch)
        self.server.register_function(self.memory_clear)

    '''
        Start serving XMLRPC thread until self.signal 
        indicated close
    '''
    def run(self):
        self.signal = True
        while self.signal:
            self.server.handle_request()

    '''
        Generate return error
            - Non RPC
    '''
    def spawn_error(self, code):
        return "RETURN_STATUS:" + self.errors[code]

    '''
        Validate a request token
            - Non RPC
    '''
    def authorize_request(self, incoming_auth_token):
        if self.auth_token != incoming_auth_token:
            logging.warning("Unauthorized access attempt")
            return False
        return True

    '''
        Request to add something to memory
            - RPC
    '''
    def memory_put(self, auth_token, remote_id, label, data):
        if not self.authorize_request(auth_token):
            return (False, self.spawn_error("AUTH"))
    
        if self.max_storage is not None:
            new_mem_size = getsizeof(self.memory) + getsizeof(data)
            if new_mem_size >= self.max_storage:
                logging.warning("Memory cap reached")
                return (False, self.spawn_error("CAP"))

        self.lock.acquire()
        try:
            # Ensure that remote_id exists as a dict
            if remote_id not in self.memory:
                self.memory[remote_id] = {}

            # Set remote_id[label] to the data
            self.memory[remote_id][label] = data
        finally:
            self.lock.release()

        return (True, self.spawn_error("OKAY"))

    '''
        Request to get something from memory
            - RPC
    '''
    def memory_fetch(self, auth_token, remote_id, label):
        if not self.authorize_request(auth_token):
            return (False, self.spawn_error("AUTH"))

        self.lock.acquire()
        try:
            return_data = self.memory[remote_id][label]
        except KeyError:
            return_data = None
        finally:
            self.lock.release()

        if return_data is None:
            return (False, self.spawn_error("KEY"))

        return (True, return_data)
        
    '''
        Request to get remove a device's memory
            - RPC
    '''
    def memory_clear(self, auth_token, remote_id):
        if not self.authorize_request(auth_token):
            return (False, self.spawn_error("AUTH"))

        self.lock.acquire()
        try:
            if remote_id in self.memory:
                logging.info("Removing a device's data")
                del self.memory[remote_id]
                return_data = self.spawn_error("OKAY")
            else:
                return_data = self.spawn_error("KEY")
        finally:
            self.lock.release()

        if return_data is None:
            return (False, self.spawn_error("KEY"))

        return (True, return_data)
