import logging
import os.path
import json
from datetime import datetime, date, timedelta
from requests import get
from requests.exceptions import ConnectionError

log = logging.getLogger('becbacnet')

logging.basicConfig(level=logging.WARNING)

headers = {
    "Accept": "application/json"
}
fmt = "%Y-%m-%d"

class EntelliwebError(Exception):
    pass

class EntelliwebUnavailable(EntelliwebError):
    pass

class EnteliwebClient(object):
    """A client for becbacnet Energy Suite API"""

    def __init__(self, base_uri, org):
        self.base_uri = base_uri
        self.org = org

    def uri(self, endpoint):
        return "{}/enteliweb/{}/{}".format(self.base_uri, self.org, endpoint)

    def get(self, *args, **kwargs):
        uri = self.uri(args[0])
        log.debug("connecting to {}".format(uri))
        try:
            return get(uri, *args[1:], **kwargs)
        except ConnectionError as exc:
            raise EntelliwebUnavailable(exc)

    def resource(self):
        response = self.get('resource', headers=headers)
        return response.json()['ResourceList']

    def consumption(self, meter_list, start_time, end_time, interval, resource, by_id=True):
        payload = {
            "meterlist[]": meter_list,
            "start": start_time.strftime(fmt),
            "end": end_time.strftime(fmt),
            "interval": interval,
            "resource": resource,
        }
        if by_id:
            payload["search"] = "id"

        response = self.get('data', params=payload, headers=headers)
        if response.status_code != 200:
            raise EntelliwebError("HTTP {}: {}".format(response.status_code, response.text))
        return response.text


    def meters(self):
        response = self.get('meter', headers=headers)
        data = response.json()
        return [{
            'identifier': m['ID'],
            'label': m['Name'],
            'description': m['Description']
        } for m in data['MeterList']]
