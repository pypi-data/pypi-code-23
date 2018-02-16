# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

import requests


BASE_URL_SEARCH = 'http://www.gipuzkoairekia.eus/api/jsonws/DOGGipuzkoaIrekiaApi-portlet.categoria/get-temas-transparencia'  # noqa

LANG_SUFFIX = {
    'es': '',
    'eu': 'EU',
}

TITLE_KEY = 'titulo'


class TransparencySectionListView(BrowserView):

    def get_language(self):
        return self.context.Language()

    def item_list(self):
        data = self.get_data()
        for item in data:
            yield self.decorate_item(item)

    def get_data(self):
        url = BASE_URL_SEARCH
        try:
            data = requests.get(url, timeout=10)
            return data.json()
        except Exception, e:
            from logging import getLogger
            log = getLogger(__name__)
            log.exception(e)
            return []

    def decorate_item(self, item):
        language = self.get_language()
        item['title'] = item.get(TITLE_KEY + LANG_SUFFIX.get(language))
        return item
