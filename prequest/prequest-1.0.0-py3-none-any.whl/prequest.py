from requests import Response
from requests import Session
from typing import Dict


class Prequest(Session):
    PARENT_API_URL = "https://t4oqhh4fk6.execute-api.us-east-1.amazonaws.com/beta?url={}&returnS3Url={}"

    def request(self, method: str, url: str, params: Dict = None, **kwargs) -> Response:
        """
        Sends a request.
        If the data for a GET is not available, it is returned from cache if possible.

        :param method: Method for the new Request object.
        :param url: URL for the new Request object.
        :param params: (optional) Dictionary or bytes to be sent in the query string for the Request.
        :param kwargs: Optional arguments that request takes.
        :return: Response object
        :rtype: requests.Response
        """

        # Default behaviour for all methods that are not GET
        if method != 'GET':
            return super().request(method, url, params, **kwargs)

        # Fetch from data source as a default
        resp = super().request('GET', url, params, **kwargs)

        if resp.status_code == 200:
            # Let Lambda cache file if necessary
            # We do not care about the response
            super().request('GET', self.PARENT_API_URL.format(url, False))

            return resp
        else:
            # The original file is no longer available online
            # Get the S3 URL from the cache, this time we do care about the response
            cache_response = super().request('GET', self.PARENT_API_URL.format(url, True))

            # If cache response is 200, return cached data.
            if cache_response.status_code == 200:
                return super().request('GET', cache_response.json()['url'])
            else:
                # If not, implies cache was never created in the first place.
                # Return original response and let user handle it
                return resp
