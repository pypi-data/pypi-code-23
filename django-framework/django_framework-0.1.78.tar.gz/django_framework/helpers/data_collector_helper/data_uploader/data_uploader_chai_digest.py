import requests
import time
from data_uploader import BaseDataUploader

class DataUploaderChaiDigest(BaseDataUploader):
    '''The goal is to make it simple for us to upload data to our servers...'''
    
    UPLOAD_URL = 'http://chai-digest.chaienergy.net'
    ALLOWED_MODIFER = ('realtimeEvent', 'greenbutton_hourly', 'power', 'energy')
    
    
    def __init__(self, uid, save = True):

        
        super(DataUploaderChaiDigest, self).__init__(uid = uid, save = save)
    
    def add_datapoint(self, timestamp, value, modifier):
        self.is_allowed_modifier(modifier = modifier)
        self.is_allowed_value(value = value, modifier = modifier)
        self._data.append({'time' : timestamp, 'value' : value, 'modifier' : modifier})
    
    def upload_to_server(self):
        self._should_save()
        for data in self.chunk_list(self._data, size = self.CHUNK_SIZE):
            message = {'uid' : self.uid, 'data' : data}
            self._upload_message(message = message)

    
    def is_allowed_value(self, value, modifier):
        if modifier == 'realtimeEvent':
            self._is_allowed_value_realtime(value)
        elif modifier == 'greenbutton_hourly':
            self._is_allowed_value_hourly(value)
            
        else:
            raise ValueError( 'Modifier not recognixed')
            
    def _is_allowed_value_realtime(self, value):
        #              sample event: [1473130991.0, 1473130997.0, 381.0, 469.0, 1]
        if len(value) != 5:
            raise ValueError('The inputted data is not valid for this type!')
        
        
    def _is_allowed_value_hourly(self, value):
        
        
        if len(value) != 3:
            # starttime is keyed seperately
            # [value, duration, count]
            #              sample hourly value: [381.0, 3600, 4]
            raise ValueError('The inputted data is not valid for this type!')
        
        
if __name__ == '__main__':
    dcd = DataUploaderChaiDigest(uid = 'test', save = True)
    
    dcd.add_datapoint(timestamp = 1, value= [100, 3600, 4], modifier = 'greenbutton_hourly')
    dcd.upload_to_server()