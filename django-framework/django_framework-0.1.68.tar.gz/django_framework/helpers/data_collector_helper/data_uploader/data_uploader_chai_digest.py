import requests
import time
from data_uploader import BaseDataUploader

class DataUploaderChaiDigest(BaseDataUploader):
    '''The goal is to make it simple for us to upload data to our servers...'''
    
    UPLOAD_URL = 'http://chai-digest.chaienergy.net'
    ALLOWED_MODIFER = ('realtimeEvent', 'energy', 'power')
    
    
    def __init__(self, uid, save = True):

        
        super(DataUploaderChaiDigest, self).__init__(uid = uid, save = save)
    
    def add_datapoint(self, timestamp, value, modifier):
        self.is_allowed_modifier(modifier = modifier)
        self.data.append({'time' : timestamp, 'value' : value, 'modifier' : modifier})
    
    def upload_to_server(self):
        self._should_save()
        for data in self.chunk_list(self.data, size = self.CHUNK_SIZE):
            message = {'uid' : self.uid, 'data' : data}
            self._upload_message(message = message)
