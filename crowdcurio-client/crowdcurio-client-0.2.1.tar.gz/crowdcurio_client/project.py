import datetime
import requests
import time

from crowdcurio_client.crowdcurio import (
    CrowdCurioAPIException, CrowdCurioObject
)

class Project(CrowdCurioObject):
    _api_slug = 'project'
    _link_slug = 'project'
    _edit_attributes = (
        'slug',
        'name',
        'short_description',
        'description',
        'avatar',
        'is_active',
        'is_featured',
        'is_external',
        'redirect_url',
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'Project', 'id': self.id}})
