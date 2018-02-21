import requests
import base64

class CryptaKingsAPI:
    """ Wrapper for CryptaKings REST API requests"""
    API_URL = "http://hostname"
    CLIENT_ID = 'test'
    CLIENT_SECRET = 'test'

    # Auth-Service Section BEGIN
    def auth_get_token(self, username, password):
        """Get OAuth token bycredentials"""
        URL = self.API_URL + 'api/oauth/token'

        headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                  }
        payload = {
                    'grant_type': 'password',
                    'client_id': self.CLIENT_ID,
                    'client_secret': self.CLIENT_SECRET,
                    'username': username,
                    'password': password
                  }
        response = requests.post(URL, headers=headers, payload=payload, allow_redirects=True)
        return response

    def auth_refresh_token(self, token):
        """Refresh given OAuth token"""
        URL = self.API_URL + 'api/oauth/token'

        headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                  }
        payload = {
                    'grant_type': 'refresh_token',
                    'client_id': self.CLIENT_ID,
                    'client_secret': self.CLIENT_SECRET,
                    'refresh_token': token
                  }
        response = requests.post(URL, headers=headers, payload=payload, allow_redirects=True)
        return response
    
    # Auth-Service Section END
    
    # User Section BEGIN
    def user_create(self, first_name, last_name, username, password):
        """Create new user with given credentials"""
        URL = self.API_URL + 'api/user/create'
        headers = {
                    'Content-Type': 'application/json'
                  }
        data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': username,
                    'password': password
               }
        response = requests.post(URL, headers=headers, data=data,
                                 allow_redirects=True)
        return response

    def user_get_all(self, token):
        """Request all users (using access token)"""
        URL = self.API_URL + 'api/user/read'
        headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer {}'.format(token)
                  }
        response = requests.post(URL, headers=headers, allow_redirects=True)
        return response
    
    # User Section END
