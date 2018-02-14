import requests
import json
import mimetypes

from xldeploy.errors import XLDeployConnectionError, XLDeployConnectionTimeout, \
    create_api_error_from_http_exception

try:
    from urllib.parse import urlparse, quote
except ImportError:
    from urlparse import urlparse
    from urllib2 import quote


class HttpClient:
    __headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Accept-Type': 'application/json'}
    
    def __init__(self, config):
        self.config = config

    def get_url(self, path=""):
        return "%s://%s:%s/%s%s" % (
            self.config.protocol, self.config.host, self.config.port, self.config.context_path, path)

    def get_credentials(self):
        return (self.config.username, self.config.password)

    def get_proxies(self):
        proxies = None
        if self.config.proxy_host and self.config.proxy_port:
            if self.config.proxy_username and self.config.proxy_password:
                proxy_host_url = urlparse(self.config.proxy_host)
                proxy_username = quote(self.config.proxy_username, safe='')
                proxy_password = quote(self.config.proxy_password, safe='')

                proxy_url = "%s://%s:%s@%s:%s" % (proxy_host_url.scheme, proxy_username, proxy_password
                                                  , proxy_host_url.hostname, self.config.proxy_port)
            else:
                proxy_url = "%s:%s" % (self.config.proxy_host, self.config.proxy_port)

            proxies = {'http': proxy_url,
                       'https': proxy_url}
        return proxies

    def authenticate(self):
        print("Connecting to the XL Deploy server at %s..." % (self.get_url()))
        response = requests.get(self.get_url() + "/server/info",
                                auth=self.get_credentials(), verify=self.config.verify_ssl)
        if response.status_code == 200:
            print("Successfully connected.")
        elif response.status_code == 401 or response.status_code == 403:
            raise ValueError("You were not authenticated correctly, did you use the correct credentials?")
        elif response.status_code == 402:
            raise ValueError(
                "License not found, invalid, or expired; see the XL Deploy logs. Please contact your XebiaLabs sales representative for a valid license")
        else:
            raise ValueError("Could contact the server at %s but received an HTTP error code %s" % (
                self.get_url(), response.status_code))

    def get(self, path, headers=__headers, params={}):
        response_data = None
        try:
            params = self.get_request_params(path, headers, params)
            response = requests.get(**params)
            response.raise_for_status()
            if response.status_code == 204:
                return
            if 199 < response.status_code < 399:
                response_data = self.__extract_response(response)
        except Exception as e:
            try:
                response_data = json.loads(response.text)
            except:
                raise self.raise_xld_exception(e)
        return response_data

    def delete(self, path, headers=__headers, params={}):
        try:
            params = self.get_request_params(path, headers, params)
            response = requests.delete(**params)
        except Exception as e:
            try:
                response = json.loads(response.text)
            except:
                raise self.raise_xld_exception(e)

        return response


    def post(self, path, headers=__headers, params={}, body=None):
        response_data = None
        try:
            if body != None and headers['Accept'] == 'application/json':
                body = json.dumps(body)
            params = self.get_request_params(path, headers, params, body)
            response = requests.post(**params)
            response.raise_for_status()
            if response.status_code == 204:
                return
            elif 199 < response.status_code < 399:
                response_data = self.__extract_response(response)
        except Exception as e:
            try:
                response_data = json.loads(response.text)
            except:
                raise self.raise_xld_exception(e)

        return response_data

    # apply DSL, POST Multiple Multipart-Encoded Files using Python requests module, see: http://docs.python-requests.org/en/master/user/advanced/#advanced
    def multipart_post(self, path, multiple_files=[]):
        response_data = None
        try:
            response = requests.post(
                    url=self.get_url(path), files=multiple_files, auth=self.get_credentials(),
                    proxies=self.get_proxies(), verify=self.config.verify_ssl)
            response.raise_for_status()
            if response.status_code == 204:
            	return
            elif 199 < response.status_code < 399:
            	response_data = self.__extract_response(response)
        except Exception as e:
            try:
                response_data = json.loads(response.text)
            except:
                raise self.raise_xld_exception(e)

        return response_data

    def put(self, path, headers=__headers, params={}, body=None):
        try:
            if body != None:
                body = json.dumps(body)
            params = self.get_request_params(path, headers, params, body)
            response = requests.put(**params)
            response.raise_for_status()
            if response.status_code == 204:
                return
            if 199 < response.status_code < 399:
                response_data = self.__extract_response(response)
        except Exception as e:
            try:
                response_data = json.loads(response.text)
            except:
                raise self.raise_xld_exception(e)

        return response_data

    def raise_xld_exception(self, e):
        if isinstance(e, requests.exceptions.Timeout):
            raise XLDeployConnectionTimeout('Timeout connecting to {0}'.format(self.config.host))
        elif isinstance(e, requests.exceptions.ConnectionError):
            raise XLDeployConnectionError('Could not connect to {0}'.format(self.config.host))
        elif isinstance(e, requests.exceptions.HTTPError):
            raise create_api_error_from_http_exception(e)
        else:
            raise e

    def __extract_response(self, response):
        if response.headers['Content-Type'] == 'application/json':
            return json.loads(response.text)
        else:
            return response.text

    def get_request_params(self, path, headers=__headers, params={}, body=None):
        params_dict = {'url': self.get_url(path), 'params': params, 'auth': self.get_credentials(), 'headers': headers,
                       'proxies': self.get_proxies(), 'verify': self.config.verify_ssl}
        if body:
            params_dict['data'] = body
        return params_dict


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
