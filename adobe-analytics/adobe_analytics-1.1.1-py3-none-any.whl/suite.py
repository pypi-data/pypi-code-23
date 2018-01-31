from __future__ import absolute_import
from __future__ import print_function

import functools

from adobe_analytics.report_downloader import ReportDownloader


class Suite(object):
    def __init__(self, name, suite_id, client):
        self.name = name
        self.id = suite_id
        self.client = client
        self._downloader = ReportDownloader(self)

    def download(self, obj):
        """ obj can be ReportDefinition, report_id (int or float) """
        return self._downloader.download(obj)

    def queue(self, definition):
        return self._downloader.queue(definition)

    def cancel(self, report_id):
        return self._downloader.cancel(report_id)

    @functools.lru_cache(maxsize=None)
    def metrics(self):
        response = self.client.request(
            api='Report',
            method='GetMetrics',
            data={
                "reportSuiteID": self.id
            }
        )
        return self._response_to_dict(response)

    @functools.lru_cache(maxsize=None)
    def dimensions(self):
        response = self.client.request(
            api='Report',
            method='GetElements',
            data={
                "reportSuiteID": self.id
            }
        )
        return self._response_to_dict(response)

    @functools.lru_cache(maxsize=None)
    def segments(self):
        response = self.client.request(
            api='Segments',
            method='Get',
            data={
                "accessLevel": "shared"
            }
        )
        return self._response_to_dict(response)

    @staticmethod
    def _response_to_dict(data):
        return {item["id"]: item for item in data}

    def __repr__(self):
        return "{name} ({id})".format(id=self.id, name=self.name)
