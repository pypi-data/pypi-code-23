import aiohttp


class SabnzbdApi(object):
    def __init__(self, base_url, api_key, web_root=''):
        if base_url.endswith('/'):
            base_url = base_url[:-1]

        web_root = web_root.strip('/') + '/'

        self.api_url = '{}/{}{}'.format(base_url, web_root, 'api')
        self.queue = {}
        self.default_params = {'apikey': api_key, 'output': 'json'}

    async def call(self, params):
        api_params = {**self.default_params, **params}
        try:
            with aiohttp.ClientSession() as session:
                resp = await session.get(self.api_url, params=api_params)
                data = await resp.json()
                if data.get('status', True) is False:
                    self.handle_error(data, api_params)
                else:
                    return data
        except aiohttp.ClientError:
            raise SabnzbdApiException('Unable to communicate with Sabnzbd API')

    async def refresh_data(self):
        queue = await self.get_queue()
        history = await self.get_history()
        totals = {}
        for k in history:
            if k[-4:] == 'size':
                totals[k] = self.convert_size(history.get(k))
        self.queue = {**totals, **queue}

    async def get_history(self):
        params = {'mode': 'history', 'limit': 1}
        history = await self.call(params)
        return history.get('history')

    async def get_queue(self):
        params = {'mode': 'queue', 'start': '0', 'limit': '10'}
        queue = await self.call(params)
        return queue.get('queue')

    async def pause_queue(self):
        params = {'mode': 'pause'}
        await self.call(params)

    async def resume_queue(self):
        params = {'mode': 'resume'}
        await self.call(params)

    async def set_speed_limit(self, speed=100):
        params = {'mode': 'config', 'name': 'speedlimit', 'value': speed}
        await self.call(params)

    async def check_available(self):
        params = {'mode': 'queue'}
        await self.call(params)
        return True

    def convert_size(self, size_str):
        suffix = size_str[-1]
        if suffix == 'K':
            multiplier = 1.0 / (1024.0 * 1024.0)
        elif suffix == 'M':
            multiplier = 1.0 / 1024.0
        elif suffix == 'T':
            multiplier = 1024.0
        else:
            multiplier = 1

        try:
            val = float(size_str.split(' ')[0])
            return val * multiplier
        except ValueError:
            return 0.0

    def handle_error(self, data, params):
        error = data.get('error', 'API call failed')
        mode = params.get('mode')
        raise SabnzbdApiException(error, mode=mode)


class SabnzbdApiException(Exception):
    def __init__(self, message, mode=None):
        self.message = message
        self.mode = mode

    def __str__(self):
        if self.mode is not None:
            msg_format = '{}: calling api endpoint \'{}\''
        else:
            msg_format = '{}'
        return msg_format.format(self.message,
                                 self.mode if self.mode is not None else '')

