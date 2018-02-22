import os
import requests as req

from requests.packages.urllib3.exceptions import InsecureRequestWarning

import json
from .picache import PICache
from .config import enable_cache, webapi_server, global_persistence, auth_config

# ignore pesky ssl warnings
req.packages.urllib3.disable_warnings(InsecureRequestWarning)


class PIObject(object):

    webapi_server = "https://sr-26716-t/piwebapi/"
    # proxy disabling
    os.environ['NO_PROXY'] = 'sr-26716-t'
    cache = PICache()

    def post(self, url, payload):
        return self.handle_response(req.post(url, json=payload, verify=False, auth=auth_config))

    def get(self, url, params={}):
        return self.handle_response(req.get(url, params=params, verify=False, auth=auth_config))

    def put(self, url, params={}):
        return self.handle_response(req.put(url, json=params, verify=False, auth=auth_config))

    def patch(self, url, params={}):
        return self.handle_response(req.patch(url, json=params, verify=False, auth=auth_config))

    def req_delete(self, url, params={}):
        return self.handle_response(req.delete(url, params=params, verify=False, auth=auth_config))

    def handle_response(self, response):

        if response.text and "Errors" in json.loads(response.text):
            raise ValueError(response.text)

        if response.status_code == 404:
            print(response.text)
            raise ValueError("404 not found")
        if response.status_code == 400:
            print(response.text)
            raise ValueError("400 bad request")

        return response

    def request(self, path, params={}, persistence=None):
        """ perform request with path, parameters and persistence
        persistence 0 means no persistence """
        if persistence is None:
            persistence = global_persistence
        
        if "sr-26716-t" in path:
            path = path.split("https://sr-26716-t/piwebapi/")[1]
        
        if "https" not in path:
            path = webapi_server+path

        if persistence > 0 and enable_cache:

            key = path+str(params)

            cached = self.cache.read(key)
            if cached:
                return json.loads(cached)
            else:
                value = self.get(path, params=params).text
                self.cache.write(key, value, persistence)
                return json.loads(value)
        else:
            # bypass cache
            return json.loads(self.get(path, params=params).text)
