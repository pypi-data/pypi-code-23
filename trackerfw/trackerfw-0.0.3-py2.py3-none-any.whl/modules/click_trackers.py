import os
import aiohttp
import aiohttp_jinja2

from urllib.parse import unquote, quote
from trackerfw.module import Module
from trackerfw.route import Route
from trackerfw.tracker_utils import top_level_extensions

__all__ = ['RedirectUris', 'BitLy']

class RedirectUris(Module):
    @property
    def routes(self):
        # TradeDoubler
        yield Route(
            self.handler,
            { 'name': 'TradeDoubler' },
            hostname='clk.tradedoubler.com',
            path='/click'
        )

        # Google
        for ext in top_level_extensions:
            yield Route(
                self.handler,
                { 'name': 'Google URL (' + ext + ')' },
                hostname='www.google' + ext,
                path='/url'
            )

        # MailRD
        yield Route(
            self.handler,
            { 'name': 'MailRD' },
            hostname='click.mailrd.net',
            path='/'
        )

    @aiohttp_jinja2.template('redirect.html')
    async def handler(self, request):
        query_keys = [
            'url',
            'href'
        ]

        for key in query_keys:
            if key in request.query:
                return {
                    'redirect_url': unquote(request.query[key])
                }

        return {
            'url': str(request.url),
            'redirect_url': None,
        }

class BitLy(Module):
    @property
    def routes(self):
        yield Route(
            self.handler,
            { 'name': 'Bit.ly' },
            hostname='bit.ly',
        )

    @aiohttp_jinja2.template('redirect.html')
    async def handler(self, request):
        endpoint = 'https://api-ssl.bitly.com/v3/expand?shortUrl=' + \
            quote(str(request.url)) + \
            '&access_token=' + \
            os.environ['BITLY_TOKEN']

        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint) as response:
                data = await response.json()

                if data['status_code'] != 200 or len(data['data']['expand']) == 0:
                    return {
                        'url': str(request.url),
                        'redirect_url': None
                    }

                return {
                    'redirect_url': unquote(data['data']['expand'][0]['long_url'])
                }
