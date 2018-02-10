import os
import aiohttp
import aiohttp_jinja2

from urllib.parse import unquote, quote
from trackerfw.handler import Handler

class BitLy(Handler):
    @aiohttp_jinja2.template('redirect.html')
    async def dispatch(self, request):
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
