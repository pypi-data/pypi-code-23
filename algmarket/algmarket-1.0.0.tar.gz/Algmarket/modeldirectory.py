'Algorithmia Data API Client (python)'

import json
import re
import six
import tempfile

import Algmarket
from Algmarket.modelfile import ModelFile
from Algmarket.model import ModelObject, ModelObjectType
from Algmarket.errors import ModelApiError
from Algmarket.util import getParentAndBase, pathJoin
from Algmarket.acl import Acl

class ModelDirectory(ModelObject):
    def __init__(self, client, modelUrl):
        super(ModelDirectory, self).__init__(ModelObjectType.directory)
        self.client = client
        # Parse dataUrl
        self.path = re.sub(r'^model://|^/', '', modelUrl)
        self.url = ModelDirectory._getUrl(self.path)

    @staticmethod
    def _getUrl(path):
        return '/v1/model/' + path

    def set_attributes(self, response_json):
        # Nothing to set for now
        pass

    def getName(self):
        _, name = getParentAndBase(self.path)
        return name

    def exists(self):
        # Heading a directory apparently isn't a valid operation
        response = self.client.getHelper(self.url)
        return (response.status_code == 200)

    def create(self, acl=None):
        '''Creates a directory, optionally include Acl argument to set permissions'''
        parent, name = getParentAndBase(self.path)
        json = { 'name': name }
        if acl is not None:
            json['acl'] = acl.to_api_param()
        response = self.client.postJsonHelper(ModelDirectory._getUrl(parent), json, False)
        if (response.status_code != 200):
            raise ModelApiError("Directory creation failed: " + str(response.content))

    def delete(self, force=False):
        # Delete from data api
        url = self.url
        if force:
            url += '?force=true'

        result = self.client.deleteHelper(url)
        if 'error' in result:
            raise ModelApiError(result['error']['message'])
        else:
            return True

    def file(self, name):
        return ModelFile(self.client, pathJoin(self.path, name))

    def files(self):
        return self._get_directory_iterator(ModelObjectType.file)

    def dir(self, name):
        return ModelDirectory(self.client, pathJoin(self.path, name))

    def dirs(self):
        return self._get_directory_iterator(ModelObjectType.directory)

    def list(self):
        return self._get_directory_iterator()

    def get_permissions(self):
        '''
        Returns permissions for this directory or None if it's a special collection such as
        .session or .algo
        '''
        response = self.client.getHelper(self.url, acl='true')
        if response.status_code != 200:
            raise ModelApiError('Unable to get permissions:' + str(response.content))
        content = response.json()
        if 'acl' in content:
            return Acl.from_acl_response(content['acl'])
        else:
            return None

    def update_permissions(self, acl):
        params = {'acl':acl.to_api_param()}
        response = self.client.patchHelper(self.url, params)
        if response.status_code != 200:
            raise ModelApiError('Unable to update permissions: ' + response.json()['error']['message'])
        return True

    def _get_directory_iterator(self, type_filter=None):
        marker = None
        first = True
        while first or (marker is not None and len(marker) > 0):
            first = False
            url = self.url
            query_params= {}
            if marker:
                query_params['marker'] = marker
            response = self.client.getHelper(url, **query_params)
            if response.status_code != 200:
                raise ModelApiError("Directory iteration failed: " + str(response.content))

            responseContent = response.content
            if isinstance(responseContent, six.binary_type):
                responseContent = responseContent.decode()

            content = json.loads(responseContent)
            if 'marker' in content:
                marker = content['marker']
            else:
                marker = None

            if type_filter is ModelObjectType.directory or type_filter is None:
                for d in self._iterate_directories(content):
                    yield d
            if type_filter is ModelObjectType.file or type_filter is None:
                for f in self._iterate_files(content):
                    yield f

    def _iterate_directories(self, content):
        directories = []
        if 'folders' in content:
            for dir_info in content['folders']:
                d = ModelDirectory(self.client, pathJoin(self.path, dir_info['name']))
                d.set_attributes(dir_info)
                directories.append(d)
        return directories

    def _iterate_files(self, content):
        files = []
        if 'files' in content:
            for file_info in content['files']:
                f = ModelFile(self.client, pathJoin(self.path, file_info['filename']))
                f.set_attributes(file_info)
                files.append(f)
        return files
