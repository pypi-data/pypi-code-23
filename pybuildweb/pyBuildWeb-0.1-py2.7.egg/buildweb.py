__author__ = 'rramchandani'

import urlparse
import requests
import json

import _utils.exceptions as custom_expections
from ._utils.jsonutils import DateTimeDecoder, DateTimeEncoder, URLDecoder
from .build import Build


class BuildWeb(object):

    _builds = None

    def __init__(self, product=None, branch=None, buildtype="ob", state=None, version=None,
                 build_api_url="http://buildapi.eng.vmware.com",
                 #build_web_url="https://buildweb.eng.vmware.com/",
                 limit=10000):
        self.product = product
        self.branch = branch
        self.buildtype = buildtype
        self.state = state
        self.version = version

        self.build_api_url = build_api_url
        #self.build_web_url = build_web_url
        self.limit = limit

    @property
    def builds(self):
        if self._builds is None:
            params = dict()
            if self.product is not None: params['product'] = self.product
            if self.branch is not None: params['branch'] = self.branch

            if self.state is not None: params['buildstate'] = self.state
            if self.version is not None: params['version'] = self.version
            if self.limit is not None: params['_limit'] = self.limit

            buildweb_url = urlparse.urljoin(self.build_api_url, "/{0}/build".format(self.buildtype))

            response = requests.get(buildweb_url, params=params)

            if response.status_code == requests.codes.ok:
                _ = json.loads(response.content, parse_int=int, parse_float=float,
                               date_format="%Y-%m-%d %H:%M:%S.%f", cls=DateTimeDecoder)
                _ = json.loads(json.dumps(_, date_format="%Y-%m-%d %H:%M:%S.%f", cls=DateTimeEncoder),
                           base_url=self.build_api_url, key_contains=["url"], cls=URLDecoder)

                if not _.has_key("_list"):
                    self._builds = []
                else:
                    self._builds = [Build(build_api_url=self.build_api_url, **i)
                                    for i in _["_list"]]

            else:
                self._builds = []
                raise custom_expections.BuildNotFound("No builds were found.\n" + \
                "  Build URL  : {0}\n".format(buildweb_url) +
                "  Params     : {0}\n".format(params) +
                "  Response   : ({0}) {1}".format(response.status_code, response.content))

        return self._builds

    def get_latest_build(self):
        return self.builds[-1]

    def get_build(self, id):
        return Build(id=id)

    def __repr__(self):
        return "<BuildWeb-{0}>".format(self.product)
