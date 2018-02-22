
import pprint


from user_login import UserLogin
from user_network import UserNetwork
from user_local_cache import UserLocalCache
from user_profile import UserProfile

class UserData(UserLogin, UserNetwork, UserLocalCache,
               UserProfile
               ):
    
    MICROSERVICE_URLS = ['http://localhost:8000']
    
    def __init__(self, base_url, username, password, profile_username = None, profile_uuid = None, profile_id = None):
        
        self.base_url = base_url
        self.username = username
        self.password = password
        self.override_username = profile_username
        self.override_uuid = profile_uuid
        self.override_id = profile_id
        
        # loginthe user! the object is now prepped!!
        self.login_as_user(profile_uuid = self.override_uuid, profile_username = self.override_username, profile_id = self.override_id)
        
        # set up the network of known models! # we might want to cache this across runs in the future
        self.get_known_models()
    

    def pretty_print(self, obj):
        
        pp = pprint.PrettyPrinter()
        pp.pprint(obj)
    


if __name__ == '__main__':
    import time
    
    starttime = time.time()
    ud = UserData(base_url = 'http://localhost:8000', username = 'test12', password = 'test12', )
    print(time.time() - starttime)
    
    print(ud.profile_username)
    print(ud.profile_uuid)
    print(ud.profile_id)
    print(time.time() - starttime)
