import asyncio
import aiohttp


class SabnzbdApi(object):
    def __init__(self, base_url, api_key):
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        self.base_url = base_url
        self.api_key = api_key
        self.queue = {}

    @asyncio.coroutine
    def refresh_queue(self):
        try:
            api_args = {
                'apikey': self.api_key,
                'mode': 'queue',
                'start': '0',
                'limit': '10',
                'output': 'json'
            }

            url = '{}/{}'.format(self.base_url, 'api')
            with aiohttp.ClientSession() as session:
                resp = yield from session.get(url, params=api_args)
                json_resp = yield from resp.json()
                self.queue = json_resp.get('queue')
        except aiohttp.ClientError:
            raise SabnzbdApiException(
                "Failed to communicate with SABnzbd API.")

    @asyncio.coroutine
    def check_available(self):
        try:
            api_args = {
                'apikey': self.api_key,
                'mode': 'qstatus',
                'output': 'json'
            }

            url = '{}/{}'.format(self.base_url, 'api')
            with aiohttp.ClientSession() as session:
                resp = yield from session.get(url, params=api_args)
                json_obj = yield from resp.json()
            if not json_obj.get('status', True):
                raise SabnzbdApiException(
                    json_obj.get('error',
                                 'Failed to communicate with SABnzbd API.'))
        except aiohttp.ClientError:
            raise SabnzbdApiException(
                "Failed to communicate with SABnzbd API.")

        return True


class SabnzbdApiException(Exception):
    pass
