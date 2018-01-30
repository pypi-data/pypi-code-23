# coding=utf-8
import logging

from .base_object import BaseObject

logger = logging.getLogger(__name__)


class MCLocation(BaseObject):
    item_url = None

    def __init__(self, json_data={}):
        self.latitude = None
        self.longitude = None
        self.gmtoff = None
        self.dstoff = None
        self.country_code = None
        self.timezone = None

        if json_data:
            self.latitude = json_data.get('latitude')
            self.longitude = json_data.get('longitude')
            self.gmtoff = json_data.get('gmtoff')
            self.dstoff = json_data.get('dstoff')
            self.country_code = json_data.get('country_code')
            self.timezone = json_data.get('timezone')

    def to_dict(self):
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'gmtoff': self.gmtoff,
            'dstoff': self.dstoff,
            'country_code': self.country_code,
            'timezone': self.timezone
        }
