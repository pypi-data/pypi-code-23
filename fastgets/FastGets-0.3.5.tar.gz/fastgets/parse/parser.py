from __future__ import absolute_import, unicode_literals
import urllib.parse

from werkzeug.utils import import_string
from werkzeug.urls import url_decode
from werkzeug.routing import Map, Rule, NotFound

from ..core.errors import NotSupported


class Parser(object):

    def __init__(self):
        self.url_map = Map(strict_slashes=False, host_matching=True,
                           redirect_defaults=False)

    def add_url_rule(self, host, rule_string, endpoint, **options):
        rule = Rule(rule_string, host=host, endpoint=endpoint, **options)
        self.url_map.add(rule)

    def parse_url(self, url_string):
        url = urllib.parse.urlparse(url_string)
        url_adapter = self.url_map.bind(server_name=url.hostname,
                                        url_scheme=url.scheme,
                                        path_info=url.path)
        query_args = url_decode(url.query)
        return url, url_adapter, query_args

    def dispatch_url(self, url_string, page_raw, **_kwargs):
        url, url_adapter, query_args = self.parse_url(url_string)
        try:
            endpoint, kwargs = url_adapter.match()
            kwargs.update(query_args)
        except NotFound:
            raise NotSupported(url_string)

        for k, v in kwargs.items():
            if isinstance(v, (tuple, list)) and len(v) == 1:
                kwargs[k] == v[0]

        kwargs.update(_kwargs)

        handler = import_string(endpoint)
        return handler(url_string, page_raw, kwargs)

    def mount_site(self, site_string):
        site = import_string(site_string)
        site.play_actions(target=self)


parser = Parser()
