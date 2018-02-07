
import requests
import urllib2

from request_session import FrameworkSession


class UserProfile(object):
    '''Login logic.  '''
    
    @property
    def profile_uuid(self):
        return self.profile['uuid']
    
    @property
    def profile_username(self):
        return self.profile['username']
    
    @property
    def profile_id(self):
        return self.profile['id']
    
    
    @property
    def profile(self):
        variable_name = 'Profile' # yes this is caps
        
        # check cache to see if the variable exists
        if self.cache.get(variable_name) != None:
            # return the cached version of the variable
            return self.cache.get(variable_name)
        
        else:
            # the cache does not have variable, fetch from servers
            response = self._get_model_data(model_name = variable_name)
            
            # save the value to cache # we override convention to get only the first entry!
            self.override_variable(variable_name = variable_name, value = response['data'][0])
            
        # return the cached version of the variable
        return self.cache.get(variable_name)