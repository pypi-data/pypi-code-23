import aiohttp
import aiohttp_jinja2

from urllib.parse import unquote, quote
from trackerfw.module import Module
from trackerfw.route import Route

__all__ = ['FacebookShareBtn']

class FacebookShareBtn(Module):
    @property
    def routes(self):
        yield Route(
            self.handler,
            { 'name': 'Facebook Share Button' },
            hostname='www.facebook.com',
            path='/plugins/share_button.php'
        )

    @aiohttp_jinja2.template('facebook-share-btn.html')
    async def handler(self, request):
        return {
            'url': quote(unquote(request.query['href']))
        }
