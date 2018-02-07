from __future__ import unicode_literals

import requests

from . import __version__, models

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

BASE_URL = 'https://api.stichtingopvoeden.nl/rest/v2/'


class Client(object):
    def __init__(self, api_key, base_url=None, session=None):
        self.base_url = base_url or BASE_URL
        self.session = session or requests.Session()
        self.session.headers['User-agent'] = 'opvoeden-api-client/{} ({})'.format(
            __version__, requests.utils.default_user_agent())
        self.session.headers['Authorization'] = api_key

    def get(self, path, object_hook=None):
        response = self.session.get(urljoin(self.base_url, path))
        response.raise_for_status()
        return response.json(object_hook=object_hook)

    def contentset_list(self):
        url = 'contentset'
        object_hook = models.ContentSet.from_dict
        response = self.get(url, object_hook=object_hook)
        return response

    def contentset(self, contentset_id):
        url = 'contentset/{}'.format(contentset_id)
        object_hook = models.Article.from_dict
        response = self.get(url, object_hook=object_hook)
        return models.ArticleNode.from_list(response)

    def article(self, external_reference):
        url = 'article/{}'.format(external_reference)
        object_hook = models.Article.from_dict
        return self.get(url, object_hook=object_hook)

    def image(self, image_id):
        url = 'image/{}'.format(image_id)
        object_hook = models.Image.from_dict
        return self.get(url, object_hook=object_hook)
