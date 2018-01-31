import datetime
import requests
import time

from crowdcurio_client.crowdcurio import CrowdCurioObject

class Response(CrowdCurioObject):
    _api_slug = 'response'
    _link_slug = 'response'
    _edit_attributes = (
        'created',
        'url',
        'content',
    )

    @classmethod
    def find(cls, id=''):
        if not id:
            return None
        return cls.where(id=id, slug=slug).next()
