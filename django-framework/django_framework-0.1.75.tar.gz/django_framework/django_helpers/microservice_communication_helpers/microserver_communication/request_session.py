import requests

class FrameworkSession():
    
    def __init__(self, base_url, view = False):
        self.BASE_URL = base_url
        if self.BASE_URL[-1] != '/':
            self.BASE_URL += '/'
        

        self.default_view = view
        self.is_session_authenticated = False
        
        self._session = None
    
    def login(self, username, password, override_username = None, override_uuid = None, override_id = None):
        self._login(username = username, password = password, override_username = override_username, override_uuid = override_uuid)
        
        if override_id:
            self._login_via_override_id(username, password, override_id = override_id)
        
    def _login_via_override_id(self, username, password, override_id):
        
        profile_uuid = None
        if override_id: # *sigh fine.
            response = self.send_query(method_type = 'GET', url = '/admin/profile/models/?filter[id]={profile_id}'.format(profile_id = override_id), view = False)
            response = response.json()
            
            if len(response['data']) > 0: # and there really shoudl only be one
                profile_uuid = response['data'][0]['uuid']
        
        if not profile_uuid:
            raise ValueError('The profile_id was not found! Check the ID or the login credentials (make sure its admin)')

        return self._login(username = username, password = password, override_uuid = profile_uuid)

    def _login(self, username, password, override_username = None, override_uuid = None):
        login_payload = dict(
            username = username,
            password = password)
        
        if override_username:
            login_payload['override'] = override_username

        elif override_uuid:
            login_payload['override_uuid'] = override_uuid
        
        
        response = self.send_query(method_type = 'POST', url = '/login/', json = login_payload, view = False)
        if response.status_code > 400:
            raise ValueError('Unable to login with the provided credentials for admin.  Or the override information provided was not valid (user not found)')
        
        self._set_session_headers(response = response)
        self.is_session_authenticated = True

        return response
    
    def _set_session_headers(self, response):
        authtoken = response.json()['data'][0]['token'] # it MUST always be this format.

        headers = { 
                    'Accept': 'application/json' ,
                    'Content-Type' : 'application/json',
                    'AUTHORIZATION' : 'Token {token}'.format(token = authtoken)
        }
        
        self.session.headers = headers
    
    @property
    def session(self):
        if self._session == None:
            self._session = requests.Session()
            
        return self._session
    
    def url_formatter(self, url, base_url = None):
        if url.find('http')>=0:
            full_url = url
        else:
            
            if url[0] == '/':
                url = url[1:]
            
            
            if base_url == None:
            
                full_url = self.BASE_URL + url
            else:
                
                if base_url[-1] != '/':
                    base_url += '/'
                
                full_url = base_url + url
            
        appender =None
        if url.find('format')>=0:
            pass
        elif url.find('?') >=0:
            appender = '&'
        else:
            appender = '?'

        if appender:
            full_url = full_url + appender + 'format=json'
        

        return full_url

    def send_query(self, method_type, url, view = None, **kwargs):
        
        response = self.session.request(method_type, url = self.url_formatter(url), **kwargs)

        if (view == None and self.default_view) or view == True:
            self.view(response = response)
        return response
    
    def view(self, response):
        
        try:
            print(response.json())
        except:
            print(response.content)

    def get(self, url, **kwargs):
        return self.send_query(method_type = 'get', url = url, **kwargs)

    def post(self, url, **kwargs):
        return self.send_query(method_type = 'post', url = url,  **kwargs)

    def put(self, url, **kwargs):
        return self.send_query(method_type = 'put', url = url,  **kwargs)

    def delete(self, url, **kwargs):
        return self.send_query(method_type = 'delete', url = url,  **kwargs)

if __name__ == '__main__':
    
    
    rs = FrameworkSession(base_url = 'http://localhost:8000/')
    
    
    password = {'username' : 'test12', 'password' : 'test12'}
    response = rs.login(username = 'test12', password = 'test12', override_id = 3)
    
    response = rs.get('profile/models/')
    
    print(response.json())
    