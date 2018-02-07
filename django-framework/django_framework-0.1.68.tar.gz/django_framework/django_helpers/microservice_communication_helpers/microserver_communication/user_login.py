
import requests
import urllib2

from request_session import FrameworkSession


class UserLogin(object):
    '''Login logic.  '''

    def login_as_user(self, profile_uuid = None, profile_username = None, profile_id = None):
        
        self.session.login(username = self.username, password = self.password, 
                            override_uuid = profile_uuid, override_username = profile_username, override_id = profile_id
                            )

    @property
    def session(self):
        
        if getattr(self, '_session', None) == None:
            self._session = None
            
        if self._session == None:
            self._session = FrameworkSession(base_url = self.base_url)

        return self._session

    @property
    def admin_session(self):
        if getattr(self, '_admin_session', None) == None:
            
            self._admin_session = None
            
        if self._admin_session is None:
            self._admin_session = FrameworkSession(base_url = self.base_url)
            self._admin_session.login(username = self.username, password = self.password) # note that the credentials might not actually be admin
            # but thats up to you.

        return self._admin_session
    
    
    
if __name__ == '__main__':
    un = UserLogin()
    un._session = None
    un.base_url = 'http://localhost:8000'
    un.username = 'test12'
    un.password = 'test12'
    un.login_as_user(profile_id = None)
