import datetime
import requests
import time

from crowdcurio_client.crowdcurio import CrowdCurioObject

class User(CrowdCurioObject):
    _api_slug = 'user'
    _link_slug = 'user'
    _edit_attributes = (
        'email',
    )

    @classmethod
    def find(cls, id=''):
        if not id:
            return None
        return cls.where(id=id).next()
