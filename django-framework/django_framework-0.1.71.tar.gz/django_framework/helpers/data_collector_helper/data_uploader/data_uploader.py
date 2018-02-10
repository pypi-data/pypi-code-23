'''
Created on Feb 5, 2018

@author: aser
'''
import requests
import time

class BaseDataUploader(object):
    '''The goal is to make it simple for us to upload data to our servers...'''
    
    UPLOAD_URL = None
    CHUNK_SIZE = 20
    ALLOWED_MODIFER = []
    
    MAX_TRY = 5  # number of times we should try to POST the data to the URL endpoint
    SLEEP_INTERVAL = 1 # how to long to wait, in seconds, between each try.  
    
    def __init__(self, uid, save = True):
        self.uid = uid
        self.save = save
        self._data = []

    
    def add_datapoint(self, datapoint):
        raise NotImplemented()
        if len(datapoint) != 3:
            raise ValueError('A datpaoint needs to be: [time, value, duration]')
        self._data.append(datapoint)

    def add_data(self, data):
        raise NotImplemented()
        for d in data:
            self.add_datapoint(datapoint = d)
    
    def upload_to_server(self):
        raise NotImplemented()
        if self._should_save() == False:
            return
        
        return
        for data in self.chunk_list(self._data, self.CHUNK_SIZE): # split the list into size of 10 so we arent overloading the server
            message= {'response' : {'data' : data, "data_type": self.greenbutton_type, "address": self.uid}}
            print(message)
            for x in xrange(self.MAX_TRY):
                try:
                    response = requests.post(self.UPLOAD_URL, json = message)
                    break
                except requests.exceptions.ConnectionError:
                    print('connection error waiting 1 second')
                    time.sleep(self.SLEEP_INTERVAL)
                    
            print(response.text)
    
    def _upload_message(self, message):
        for x in xrange(5):
            try:
                response = requests.post(self.UPLOAD_URL, json = message)
                break
            except requests.exceptions.ConnectionError:
                print('connection error waiting 1 second')
                time.sleep(1)
                
        print(response.text)
    
    
    def _should_save(self):
        should_save =  True
        if len(self._data) == 0:
            print('no data to save')
            should_save = False
        
        if self.save != True:  # we break it here for checking purposes etc.  After that data is uploaded to server!
            print('Turned off saving feature probably for debugging purposes.')
            should_save = False
            
        return should_save
    
    
    def chunk_list(self, alist, size):
        
        """Yield successive n-sized chunks from l."""
        for i in xrange(0, len(alist), size):
            yield alist[i:i+size]
            
            
    def is_allowed_modifier(self, modifier):
        if modifier not in self.ALLOWED_MODIFER:
            raise ValueError('The modifier you are trying to use is not allowed for this Uploader : ' + str(self.ALLOWED_MODIFER))