"""user.py contains basic information about the steno3d user"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import properties


class User(properties.HasProperties):
    """Class representing a user instance"""
    _model_api_location = "user"

    email = properties.GettableProperty(
        doc='Email',
    )
    name = properties.GettableProperty(
        doc='Name',
    )
    url = properties.GettableProperty(
        doc='URL',
    )
    affiliation = properties.GettableProperty(
        doc='Affiliation',
    )
    location = properties.GettableProperty(
        doc='Location',
    )
    username = properties.GettableProperty(
        doc='Username',
    )

    devel_key = properties.GettableProperty(
        doc='Developer API Key',
    )

    file_size_limit = properties.GettableProperty(
        doc='Inidividual file limit',
    )
    project_size_limit = properties.GettableProperty(
        doc='Project size limit',
    )
    project_resource_limit = properties.GettableProperty(
        doc='Maximum resources in a project',
    )

    def login_with_json(self, login_json):
        self._backend['username'] = login_json['uid']
        self._backend['email'] = login_json['email']
        self._backend['name'] = login_json['name']
        self._backend['url'] = login_json['url']
        self._backend['affiliation'] = login_json['affiliation']
        self._backend['location'] = login_json['location']
        self._backend['file_size_limit'] = login_json.get(
            'file_size_limit', 26214400
        )
        self._backend['project_size_limit'] = login_json.get(
            'project_size_limit', 104857600
        )
        self._backend['project_resource_limit'] = login_json.get(
            'project_resource_limit', 100
        )

    def set_key(self, devel_key):
        self._backend['devel_key'] = devel_key

    def logout(self):
        self._backend.pop('username', None)
        self._backend.pop('email', None)
        self._backend.pop('name', None)
        self._backend.pop('url', None)
        self._backend.pop('affiliation', None)
        self._backend.pop('location', None)
        self._backend.pop('devel_key', None)
        self._backend.pop('file_size_limit', None)
        self._backend.pop('project_size_limit', None)
        self._backend.pop('project_resource_limit', None)

    @property
    def logged_in(self):
        return self.username is not None
