import aiohttp_jinja2

from urllib.parse import unquote, urlparse, parse_qs
from trackerfw.handler import Handler

class ClickTracker(Handler):
    @aiohttp_jinja2.template('redirect.html')
    async def dispatch(self, request):
        query_keys = [
            'url',
            'href',
            'q'
        ]

        if 'u3' in request.query:
            query = parse_qs(urlparse(unquote(request.query['u3'])).query)

            return {
                'redirect_url': unquote(query['u'][0])
            }

        for key in query_keys:
            if key in request.query:
                return {
                    'redirect_url': unquote(request.query[key])
                }

        return {
            'url': str(request.url),
            'redirect_url': None,
        }