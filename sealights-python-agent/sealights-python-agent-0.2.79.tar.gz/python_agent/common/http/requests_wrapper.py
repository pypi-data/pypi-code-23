from python_agent.packages import requests


class Requests(object):
    def __init__(self, config_data):
        self.config_data = config_data

    def patch_request(self, url, patch_content_type, kwargs):
        kwargs.update({
            "verify": False,
            "timeout": 120
        })
        if self.config_data.proxy:
            kwargs["proxies"] = {
                "http": self.config_data.proxy,
                "https": self.config_data.proxy
            }
        headers = kwargs.setdefault("headers", {})
        if patch_content_type:
            headers["Content-Type"] = "application/json"
        headers["Authorization"] = "Bearer %s" % self.config_data.token
        return self.config_data.server + url

    def get(self, url, params=None, patch_content_type=True, **kwargs):
        url = self.patch_request(url, patch_content_type, kwargs)
        return requests.get(url, params=params, **kwargs)

    def post(self, url, data=None, json=None, patch_content_type=True, **kwargs):
        url = self.patch_request(url, patch_content_type, kwargs)
        return requests.post(url, data=data, json=json, **kwargs)

    def put(self, url, data=None, patch_content_type=True, **kwargs):
        url = self.patch_request(url, patch_content_type, kwargs)
        return requests.put(url, data=data, **kwargs)

    def patch(self, url, data=None, patch_content_type=True, **kwargs):
        url = self.patch_request(url, patch_content_type, kwargs)
        return requests.patch(url, data=data, **kwargs)

    def delete(self, url, patch_content_type=True, **kwargs):
        url = self.patch_request(url, patch_content_type, kwargs)
        return requests.delete(url, **kwargs)
