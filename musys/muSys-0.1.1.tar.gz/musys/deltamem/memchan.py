import dill
import logging
import xmlrpc.client

'''
    Memory Channel - For interacting with network-based memory
'''
class memchan:
    def __init__(self, auth_token, port, local_id, host=None):
        try:
            self.port = int(port)
            self.auth_token = str(auth_token)
            self.local_id = str(local_id)
        except ValueError as _err:
            logging.error(_err)
            raise
        if self.port < 1 or self.port > 65535:
            logging.error("Port number out of range")
            raise Exception("Invalid port")

        self.port = str(self.port)
        if host is not None:
            self.host = "http://"+host+":"+self.port
        else:
            self.host = "http://localhost:"+self.port
        
        self.accessor = xmlrpc.client.ServerProxy(self.host)

    '''
        Store data on the network attatched memory
    '''
    def put(self, label, data):
        if type(label) != str:
            logging.error("Label must be type 'string'")
            return None
        
        if type(data) != bytes:
            data = dill.dumps(data)

        result = self.accessor.memory_put(
            self.auth_token, 
            self.local_id,
            label,
            data
            )
        
        if not result[0]:
            logging.error(result[1])
            return None
        else:
            return True
        
    '''
        Get data from the network attatched memory
    '''
    def fetch(self, label):
        if type(label) != str:
            logging.error("Label must be type 'string'")
            return None

        result = self.accessor.memory_fetch(
            self.auth_token,
            self.local_id,
            label
        )

        if not result[0]:
            logging.error(result[1])
            return None
        else:
            # XMLRPC takes the dilled data and bins it,
            # so we have to .data it before loads
            return dill.loads(result[1].data) 

    '''
        Delete memory belonging to this instance 
        from the network attatched memory
    '''
    def memory_clear(self):
        self.accessor.memory_clear(
            self.auth_token,
            self.local_id
        )
