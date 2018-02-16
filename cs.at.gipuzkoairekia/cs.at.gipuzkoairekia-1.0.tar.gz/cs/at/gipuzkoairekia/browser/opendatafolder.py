# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from cs.at.gipuzkoairekia.interfaces import IGipuzkoaIrekiaFolder
from lxml import etree
from plone.batching import Batch
from plone.memoize.ram import cache
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import time


BASE_URL_SEARCH = 'http://api.gipuzkoairekia.eus/dataset/buscar?org={0}&numRes=9999' # noqa
BASE_URL_DATASET = 'http://api.gipuzkoairekia.eus/dataset/{0}'

CATEGORY_SEARCH_URL = 'http://api.gipuzkoairekia.eus/categoria/lista'

LANG_SUFFIX = {
    'es': '',
    'eu': 'Eu',
    'en': 'En'
}

TITLE_KEY = 'titulo'
DESCRIPTION_KEY = 'descripcion'
SOURCE_KEY = 'fuente'
NAME_KEY = 'nombre'


def _render_dataset_id(method, self, datasetid):
    return (datasetid, time.time() // 3600)


def _render_organization_id(method, self):
    return (self.get_organization_id(), time.time() // 3600)


@implementer(IPublishTraverse)
class OpenDataFolderView(BrowserView):

    temp = ViewPageTemplateFile('opendatafolder.pt')

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
        data = self.dataset_data()
        return data.get('title', '')

    def subpath_description(self):
        data = self.dataset_data()
        return data.get('description', '')

    def get_organization_id(self):
        context = aq_inner(self.context)
        while not (IGipuzkoaIrekiaFolder.providedBy(context) or IPloneSiteRoot.providedBy(context)): # noqa
            context = aq_parent(context)

        if IGipuzkoaIrekiaFolder.providedBy(context):
            return context.getField('institution_code').get(context)
        else:
            return None

    @cache(_render_organization_id)
    def category_data(self):
        try:
            return etree.parse(CATEGORY_SEARCH_URL).getroot()
        except Exception, e:
            from logging import getLogger
            log = getLogger(__name__)
            log.exception(e)
            return {'error': True}

    def get_category(self, id):
        language = self.get_language()
        categories = self.category_data()
        items = categories.xpath('//categoria')
        new_data = {}
        for item in items:
            category_id = item.xpath('id')[0].text
            category_title = item.xpath('{0}'.format(TITLE_KEY + LANG_SUFFIX.get(language)))[0].text # noqa
            new_data[category_id] = category_title

        return new_data.get(id, '')

    @cache(_render_organization_id)
    def organization_data(self):
        organization = self.get_organization_id()
        url = BASE_URL_SEARCH.format(organization)
        try:
            return etree.parse(url).getroot()
        except Exception, e:
            from logging import getLogger
            log = getLogger(__name__)
            log.exception(e)
            return {'error': True}

    def dataset_data(self):
        language = self.get_language()
        data = self.one_dataset_data(self.subpath[0])
        for dataset in data.xpath('//dataset'):
            item = {}
            for child in dataset.getchildren():
                if child.tag == TITLE_KEY + LANG_SUFFIX.get(language):
                    item['title'] = child.text
                elif child.tag == DESCRIPTION_KEY + LANG_SUFFIX.get(language):
                    item['description'] = child.text
                elif child.tag == SOURCE_KEY + LANG_SUFFIX.get(language):
                    item['source'] = child.text
                elif child.tag == 'recursos':
                    resources = []
                    for resource in child.getchildren():
                        new_resource = {}
                        for grandchild in resource.getchildren():
                            if grandchild.tag == NAME_KEY + LANG_SUFFIX.get(language): # noqa
                                new_resource['name'] = grandchild.text
                            elif grandchild.tag == DESCRIPTION_KEY + LANG_SUFFIX.get(language): # noqa
                                new_resource['description'] = grandchild.text
                            else:
                                new_resource[grandchild.tag] = grandchild.text

                        resources.append(new_resource)

                    item['resources'] = resources

                elif child.tag not in ['etiquetas', 'localizacion']:
                    item[child.tag] = child.text

            return item

    @cache(_render_dataset_id)
    def one_dataset_data(self, dataset):
        url = BASE_URL_DATASET.format(dataset)
        try:
            return etree.parse(url).getroot()
        except Exception, e:
            from logging import getLogger
            log = getLogger(__name__)
            log.exception(e)
            return {'error': True}

    def datasets(self):
        data = self.organization_data()
        datasets = data.xpath('//dataset')
        datasets = [self.decorate_dataset(dataset) for dataset in datasets]
        b_size = self.request.get('b_size', 20)
        b_start = self.request.get('b_start', 0)
        return Batch(datasets, b_size, b_start)

    def get_language(self):
        return self.context.Language()

    def decorate_dataset(self, item):
        language = self.get_language()
        new_item = {}
        for child in item.getchildren():
            if child.tag == TITLE_KEY + LANG_SUFFIX.get(language):
                new_item['title'] = child.text
            elif child.tag == DESCRIPTION_KEY + LANG_SUFFIX.get(language):
                new_item['description'] = child.text
            elif child.tag == SOURCE_KEY + LANG_SUFFIX.get(language):
                new_item['source'] = child.text
            elif child.tag not in ['etiquetas', 'recursos']:
                new_item[child.tag] = child.text

        return new_item
