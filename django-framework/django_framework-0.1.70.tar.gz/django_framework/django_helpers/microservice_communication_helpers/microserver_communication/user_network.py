
import requests
import urllib2

from request_session import FrameworkSession
import pprint

class UserNetwork(object):
    '''Login logic.  '''
    MICROSERVICE_URLS = []
    MICROSERVICE_MODELS = {} # declare this up top so we can avoid circular lookups when used with UserCache
    
    def __init__(self):
        self.known_models = {}
        self.get_known_models()
    
    def get_known_models(self):

        for base_url in self.MICROSERVICE_URLS:
            if base_url == 'http://localhost:8000':
                self.load_local_host_url()
                continue
            
            
            url = base_url + '/docs/endpoints/?format=json'
            
            print('url', url)
            response = requests.get(url)
            
            data = response.json()['data']
            
            models = data['models']
            special_urls = data['urls']
            
            for model in models:
                if self.MICROSERVICE_MODELS.get(model) == None:
                    self.MICROSERVICE_MODELS[model] = {'base_url' : base_url, 'multiple_urls' : []}
                
                else:
                    if self.MICROSERVICE_MODELS[model]['base_url'] != base_url:
                        self.MICROSERVICE_MODELS[model]['multiple_urls'].append(base_url)
    
    
    def load_local_host_url(self):
        
        adict = {u'AuthToken': {'base_url': 'http://localhost:8000', 'multiple_urls': []},
         u'BasicProfileRun': {'base_url': 'http://localhost:8000',
                              'multiple_urls': []},
         u'BasicTestRun': {'base_url': 'http://localhost:8000', 'multiple_urls': []},
         u'Job': {'base_url': 'http://localhost:8000', 'multiple_urls': []},
         u'Profile': {'base_url': 'http://localhost:8000', 'multiple_urls': []},
         u'User': {'base_url': 'http://localhost:8000', 'multiple_urls': []}}
        
        self.MICROSERVICE_MODELS.update(adict)
        
    
if __name__ == '__main__':
    
    un = UserNetwork()
    un.get_known_models()