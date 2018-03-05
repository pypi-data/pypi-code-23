import time

try:
    from cassandra.cluster import named_tuple_factory
    from cassandra.cluster import Cluster
except:
    print('it seems cassandra might not be installed!')
    raise


class CassandraInterface(object):
    
    def __init__(self, db_alias = None, ip = None, port= None, keyspace = None):
        
        if db_alias != None:
            ip = db_alias['ip']
            port = db_alias['port']
            keyspace = db_alias['keyspace']
            
        
        self.ip = ip
        self.port = port
        self.keyspace = keyspace
        if type(self.ip) == list:
            pass
        else:
            self.ip = [self.ip]
        self.cluster =  Cluster(self.ip, port = self.port)
        
        self.session = None
        self._is_connected = False
        
    def connect(self):
        self.session = self.cluster.connect(self.keyspace)
        self.session.default_fetch_size = 100000 # give us about 1 day of 1 second data
        
        self._is_connected = True
        
    def set_fetch_size(self, size = 100000):
        if not self._is_connected:
            self.connect()
        self.session.default_fetch_size = 100000 # give us about 1 day of 1 second data
        
        
    def kill(self):
        self.cluster.shutdown()
        self._is_connected = False
        
    def prepare_statement(self, query):
        
        if not self._is_connected:
            self.connect()

        prepared_query = self.session.prepare(query)
        return prepared_query
    
        
#     def _prepare_select_statements(self, table): # these are for raw queries!
#         qu_recent = """SELECT * FROM {tablename} WHERE uid=? AND stream_type=? ORDER BY time DESC LIMIT 1;""".format(tablename = table)
#         self.prepared_recent = self.prepare_statement(qu_recent)
# 
#         qu_first = """SELECT * FROM {tablename} WHERE uid=? AND stream_type=? ORDER BY time ASC LIMIT 1;""".format(tablename = table)
#         self.prepared_first = self.prepare_statement(qu_first)
#         
#         qu_range = """SELECT * FROM {tablename} WHERE uid=? AND stream_type=? AND time< ? AND time > ?;""".format(tablename = table)
#         self.prepared_range = self.prepare_statement(qu_range)

    def send_query(self, query): # these are for raw queries!
        if not self._is_connected:
            self.connect()
#         print(query)
        response = self.session.execute(query)
        return response
    
    
    def send_query_async(self, query):
        if not self._is_connected:
            self.connect()
        future_response = self.session.execute_async(query = query)
        return future_response
    
    
if __name__ == '__main__':
    pass