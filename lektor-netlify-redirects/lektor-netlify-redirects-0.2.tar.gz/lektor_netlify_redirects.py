# -*- coding: utf-8 -*-
from lektor.pluginsystem import Plugin
from lektor.db import Query, F
from lektor.utils import get_cache_dir
from lektor.project import Project
from lektor.publisher import Publisher

from urllib import quote_plus
import os, shutil


class CopyPublisher(Publisher):

    def publish(self, target_url, credentials=None, **extra):
        pad = self.env.new_pad()
        myQuery = Query('/', pad)
        items = myQuery.filter(F._model == 'portal')
        output_location = self.output_path

        with open('{}/_redirect'.format(output_location), 'wb') as redirect_file:
            for item in items:
                for block in item['body'].blocks:
                    try:
                        status = block['status']
                    except KeyError as e:
                        status = ''
                    try:
                        slug = quote_plus(block['slug'])
                        redirect_file.write("{} {} {}".format(
                        "/{}/{}".format(item['_slug'], slug),
                        block['url'], status))
                    except KeyError as e:
                        yield 'skipping {}'.format(block['title'])


class NetlifyRedirectsPlugin(Plugin):
    name = u'Netlify Redirects'
    description = u'Automatically creates redirects on netlify'

    def on_setup_env(self, **extra):
        self.env.add_publisher('copy', CopyPublisher)

    def on_process_template_context(self, context, **extra):
        def test_function():
            return 'Value from plugin %s' % self.name
        context['test_function'] = test_function
