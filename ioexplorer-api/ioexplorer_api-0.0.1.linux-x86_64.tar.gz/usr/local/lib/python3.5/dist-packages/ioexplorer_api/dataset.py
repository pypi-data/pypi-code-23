import requests
from ioexplorer_api import API_URL
import os
from datetime import datetime

class Dataset(object):
    def __init__(self, name, keywords, description):
        self.name = name
        self.keywords = keywords
        self.description = description

    def create(self):
        endpoint = os.path.join(API_URL, 'datasets', 'dataset')
        data = {
            "name": self.name,
            "keywords": self.keywords,
            "description": self.description
        }
        r = requests.post(endpoint, json=data)
        if r.status_code == 201:
            return r.text
        else:
            raise Exception(r.text)
