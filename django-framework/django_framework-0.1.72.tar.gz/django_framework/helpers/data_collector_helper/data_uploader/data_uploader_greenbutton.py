'''
Created on Feb 5, 2018

@author: aser
'''
import requests
import time
from data_uploader import BaseDataUploader

class DataUploaderGreenbutton(BaseDataUploader):
    '''The goal is to make it simple for us to upload data to our servers...'''
    
    UPLOAD_URL = 'http://greenbutton.chaienergy.net'
    ALLOWED_MODIFER = ['electric']
    
    def __init__(self, uid, greenbutton_type = 'electric', save = True):
        self.greenbutton_type = 'electric'
        super(DataUploaderGreenbutton, self).__init__(uid = uid, save = save)
    
    def add_datapoint(self, datapoint):
        if len(datapoint) != 3:
            raise ValueError('A datpaoint needs to be: [time, value, duration]')
        self._data.append(datapoint)

    def add_data(self, data):
        for d in data:
            self.add_datpaoint(datapoint = d)
    
    def upload_to_server(self):
        save = self._should_save()

        for data in self.chunk_list(self._data, self.CHUNK_SIZE): # split the list into size of 10 so we arent overloading the server
            message= {'response' : {'data' : data, "data_type": self.greenbutton_type, "address": self.uid}}
            if save == True:
                self._upload_message(message = message)
            else:
                print('not saved', message)
