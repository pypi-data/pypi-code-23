
import os
import json
import urlparse
import requests

import _utils.exceptions as custom_expections

from ._utils.jsonutils import URLDecoder, DateTimeDecoder, DateTimeEncoder


class Deliverable(object):

    def __init__(self, *args, **kwargs):
        """
        {u'_build_url': u'http://buildapi.eng.vmware.com/ob/build/4913138/',
         u'_currenttime': u'2017-01-12 06:31:59.281285',
         u'_download_url': u'http://buildweb.eng.vmware.com/ob/api/4913138/deliverable/?file=publish/cds/packages/UEM-Agent/463/metadata.xml.gz',
         u'_this_resource': u'deliverable',
         u'_this_url': u'http://buildapi.eng.vmware.com/ob/deliverable/458683456/',
         u'deliverable_class': u'external',
         u'id': 458683456,
         u'path': u'publish/cds/packages/UEM-Agent/463/metadata.xml.gz',
         u'size_in_mb': 1}
         """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def download(self, at_path):
        if os.path.isfile(at_path) or not os.path.isdir(at_path):
            raise IOError("Input path '{0}' is a file location.".format(at_path))

        deliverable_path = at_path

        deliverable_filename = os.path.basename(self.path)

        if not os.path.exists(deliverable_path):
            try:
                os.makedirs(deliverable_path)
            except Exception as err:
                raise err.__class__(err.message)

        response = requests.get(self._download_url, stream=True)
        if response.status_code == requests.codes.ok:
            with open(os.path.join(deliverable_path, deliverable_filename), "wb+") as fh:
                for chunk in response:
                    fh.write(chunk)
        else:
            raise IOError("Unable to download the file from url: {0}".format(self._download_url))

    @property
    def name(self):
        if hasattr(self, 'path') and isinstance(self.path, basestring):
            return os.path.basename(self.path)
        return ""

    def __getitem__(self, item):
        return self.__dict__[item]

    def __repr__(self):
        return "<Deliverable-{0}({1})>".format(self.name, self._build_url.split('/')[-2])


class Build(object):

    def __init__(self, id, buildsystem="ob",
                 build_api_url="http://buildapi.eng.vmware.com", **kwargs):
        self.id = id
        self.buildsystem = buildsystem
        self.build_api_url = build_api_url
        #self.build_web_url = build_web_url

        self.__dict__.update(**kwargs)

        self._build_details = None
        self._deliverables = None

    def __getattr__(self, item):
        if self._build_details is None:
            self._build_details = self._get_build_details()
        if hasattr(self, item):
            return self.__dict__[item]
        else:
            raise AttributeError("Attribute {0} was found.".format(item))

    def _get_build_details(self):
        url = urlparse.urljoin(self.build_api_url, "/{0}/build/{1}".format(self.buildsystem, self.id))
        response = requests.get(url)
        if response.status_code == requests.codes.ok:

            _ = json.loads(response.content,
                                 parse_int=int, parse_float=float,
                                 date_format="%Y-%m-%d %H:%M:%S.%f", cls=DateTimeDecoder)

            details = json.loads(
                json.dumps(_,
                           date_format="%Y-%m-%d %H:%M:%S.%f", cls=DateTimeEncoder),
                base_url=self.build_api_url, key_contains=["url"], cls=URLDecoder)

        else:
            raise custom_expections.BuildError("Not a valid Build ID.")

        self.__dict__.update(details)
        return details

    @property
    def deliverables(self):
        if self._deliverables is None:
            deliverables_url = getattr(self, '_deliverables_url', None)
            if deliverables_url is None:
                raise ValueError
            else:
                response = requests.get(deliverables_url)
                if response.status_code == requests.codes.ok:
                    _ = json.loads(response.content,
                                   parse_int=int, parse_float=float,
                                   date_format="%Y-%m-%d %H:%M:%S.%f", cls=DateTimeDecoder)

                    self._deliverables = json.loads(
                        json.dumps(_,
                                   date_format="%Y-%m-%d %H:%M:%S.%f", cls=DateTimeEncoder),
                        base_url=self.build_api_url, key_contains=["url"], cls=URLDecoder)
        _ = self._deliverables["_list"] if self._deliverables.has_key("_list") else []
        return [Deliverable(**item) for item in _]

    def download_deliverables(self, at_path):
        for deliverable in self.deliverables:
            deliverable_path = os.path.join(at_path, os.path.dirname(deliverable["path"]))
            deliverable_filename = os.path.basename(deliverable["path"])

            if not os.path.exists(deliverable_path):
                os.makedirs(deliverable_path)

            response = requests.get(deliverable["_download_url"])

            if response.status_code == requests.codes.ok:
                with open(os.path.join(deliverable_path, deliverable_filename), "wb+") as fh:
                    for chunk in response:
                        fh.write(chunk)
            else:
                raise custom_expections.BuildDownloadError(
                    "Unable to download the file from url: {0}, provided by BuildAPI."\
                              .format(deliverable["_download_url"]))

    def __repr__(self):
        return "<Build-{0}>".format(self.id)

    @property
    def full_version(self):
        return str(self.version) + "." + str(self.prodbuildnum)


if __name__ == "__main__":
    build = Build(id=4913138)
    from pprint import pprint

    deliverables = build.deliverables

    pprint(deliverables)

    for deliverable in deliverables:
        if deliverable.name.__contains__("VMware User Environment Manager") and deliverable.name.__contains__("x86"):
            deliverable.download("C:\\temp")
