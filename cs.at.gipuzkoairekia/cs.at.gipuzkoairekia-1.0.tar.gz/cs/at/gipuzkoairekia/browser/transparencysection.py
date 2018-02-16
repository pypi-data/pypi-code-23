# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from cs.at.gipuzkoairekia.interfaces import IGipuzkoaIrekiaFolder
from itertools import izip
from lxml import etree
from plone.batching import Batch
from plone.memoize.ram import cache
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import datetime
import requests
import time


BASE_URL_SEARCH = 'http://www.gipuzkoairekia.eus/api/jsonws/DOGGipuzkoaIrekiaApi-portlet.contenido-web/get-transparencias/group-id/{}/category-id/{}'  # noqa
BASE_URL_DATASET = 'http://www.gipuzkoairekia.eus/api/jsonws/DOGGipuzkoaIrekiaApi-portlet.contenido-web/get-transparencia/article-id/{}'  # noqa

LANG_SUFFIX = {
    'es': '',
    'eu': 'EU',
}

LANG_VALUE = {
    'es': 'es_ES',
    'eu': 'eu_ES',
}

TITLE_KEY = 'titulo'
DESCRIPTION_KEY = 'descripcion'
SOURCE_KEY = 'fuente'
NAME_KEY = 'nombre'


def _render_dataset_id(method, self, datasetid):
    return (datasetid, time.time() // 3600)


def _render_organization_id(method, self):
    return (self.get_organization_id(), self.get_category_id(), time.time() // 3600)  # noqa


@implementer(IPublishTraverse)
class TransparencySectionView(BrowserView):

    temp = ViewPageTemplateFile('transparencysection.pt')

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []

        self.subpath.append(name)
        return self

    def __call__(self):
        return self.temp(self.context)

    def is_subpath(self):
        return hasattr(self, 'subpath') and bool(self.subpath)

    def subpath_title(self):
        data = self.dataset_data_big()
        return data.get('newtitle', '')

    def subpath_description(self):
        data = self.dataset_data_big()
        return data.get('description', '')

    def get_organization_id(self):
        context = aq_inner(self.context)
        while not (IGipuzkoaIrekiaFolder.providedBy(context) or IPloneSiteRoot.providedBy(context)):  # noqa
            context = aq_parent(context)

        if IGipuzkoaIrekiaFolder.providedBy(context):
            return context.getField('group_id').get(context)
        else:
            return None

    def get_category_id(self):
        return self.context.getField('category_id').get(self.context)

    @cache(_render_organization_id)
    def organization_data(self):
        group = self.get_organization_id()
        category = self.get_category_id()
        url = BASE_URL_SEARCH.format(group, category)
        try:
            data = requests.get(url, timeout=10)
            return data.json()
        except Exception, e:
            from logging import getLogger
            log = getLogger(__name__)
            log.exception(e)
            return {'error': True}

    def dataset_data_big(self):
        article_id = self.subpath[0]
        for dataset in self.datasets():
            if dataset['articleId'] == article_id:
                return dataset

        return {}

    def dataset_data(self):
        item = self.one_dataset_data(self.subpath[0])
        if item.get('error', False):
            return {}
        else:
            return self.decorate_dataset_to_show(item)

    def decorate_dataset_to_show(self, dataset):
        language = self.get_language()
        dataset['title'] = dataset.get(TITLE_KEY + LANG_SUFFIX.get(language))
        dataset['description'] = dataset.get(DESCRIPTION_KEY + LANG_SUFFIX.get(language))  # noqa
        dataset['source'] = dataset.get(SOURCE_KEY + LANG_SUFFIX.get(language))  # noqa
        new_resources = []

        for resource in dataset.get('recursos', {}).get('recurso', []):
            new_resource = resource
            new_resource['name'] = resource.get(NAME_KEY + LANG_SUFFIX.get(language))  # noqa
            new_resource['description'] = resource.get(DESCRIPTION_KEY + LANG_SUFFIX.get(language))  # noqa
            new_resources.append(new_resource)

        if 'recursos' not in dataset:
            dataset['recursos'] = {}

        dataset['recursos']['recurso'] = new_resources
        return dataset

    @cache(_render_dataset_id)
    def one_dataset_data(self, dataset):
        url = BASE_URL_DATASET.format(dataset)
        try:
            data = requests.get(url, timeout=10)
            return data.json()
        except Exception, e:
            from logging import getLogger
            log = getLogger(__name__)
            log.exception(e)
            return {'error': True}

    def datasets(self):
        data = [self.decorate_dataset(dataset) for dataset in self.organization_data()]  # noqa
        b_size = self.request.get('b_size', 20)
        b_start = self.request.get('b_start', 0)
        return Batch(data, b_size, b_start)

    def get_language(self):
        return self.context.Language()

    def decorate_dataset(self, item):
        language = self.get_language()
        item['newtitle'] = self.parse_title(item.get('title'), language)
        item['description'] = self.parse_description(
            item.get('content'), language
        )
        item['text'] = self.parse_content(item.get('content'), language)
        item['modified'] = self.convert_date(item.get('modifiedDate'))
        item['created'] = self.convert_date(item.get('createDate'))
        return item

    def parse_title(self, content, language):
        try:
            root = etree.fromstring(safe_unicode(content).encode('utf-8'))
            values = root.xpath('/root/Title')
            for value in values:
                lang_value = value.get('language-id', None)
                if lang_value == LANG_VALUE.get(language):
                    return value.text
            return content

        except Exception, e:
            from logging import getLogger
            log = getLogger(__name__)
            log.exception(e)
            return content

    def parse_description(self, content, language):
        try:
            root = etree.fromstring(safe_unicode(content).encode('utf-8'))
            values = root.xpath("/root/dynamic-element[@name='descripcion-transparencia']/dynamic-content")  # noqa
            for value in values:
                lang_value = value.get('language-id', None)
                if lang_value == LANG_VALUE.get(language):
                    return value.text

            return content
        except Exception, e:
            from logging import getLogger
            log = getLogger(__name__)
            log.exception(e)
            return content

    def parse_content(self, content, language):
        def pairwise(iterable):
            """s -> (s0, s1), (s2, s3), (s4, s5), ..."""
            a = iter(iterable)
            return izip(a, a)

        try:
            response = []
            html_response = ''
            root = etree.fromstring(safe_unicode(content).encode('utf-8'))
            values = root.xpath("/root/dynamic-element[@name='descripcion-dato-transparencia']//dynamic-content")  # noqa
            for value in values:
                lang_value = value.get('language-id', None)
                if lang_value == LANG_VALUE.get(language) and value.text:
                    response.append(safe_unicode(value.text).encode('utf-8'))

            html_response = '<ul>'
            for first, second in pairwise(response):
                html_response += '<li>'
                html_response += '<a href="{0}">{1}</a>'.format(second, first)
                html_response += '</li>'

            html_response += '</ul>'
            return html_response
        except Exception, e:
            from logging import getLogger
            log = getLogger(__name__)
            log.exception(e)
            return content

    def convert_date(self, unixtimemiliseconds):
        try:
            value = int(unixtimemiliseconds)
            unixtime = value / 1000
            date = datetime.datetime.utcfromtimestamp(unixtime)
            return date.isoformat()
        except Exception, e:
            from logging import getLogger
            log = getLogger(__name__)
            log.exception(e)

            now = datetime.datetime.now()
            return now.isoformat()
