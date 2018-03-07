"""
   Copyright 2018 Globo.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from globomap_api_client.base import Base


class Document(Base):

    def post(self, kind, collection, document):
        uri = '{}/{}/'.format(kind, collection)
        return self.make_request(method='POST', uri=uri, data=document)

    def get(self, kind, collection, key):
        uri = '{}/{}/{}'.format(kind, collection, key)
        return self.make_request(method='GET', uri=uri)

    def search(self, kind, collection, query=None, per_page=10, page=1):
        uri = '{}/{}'.format(kind, collection)
        params = {
            'query': query,
            'per_page': per_page,
            'page': page
        }
        return self.make_request(method='GET', uri=uri, params=params)

    def list(self, kind, collection, per_page=10, page=1):
        uri = '{}/{}'.format(kind, collection)
        params = {
            'per_page': per_page,
            'page': page
        }
        return self.make_request(method='GET', uri=uri, params=params)

    def put(self, kind, collection, key, document):
        uri = '{}/{}/{}/'.format(kind, collection, key)
        return self.make_request(method='PUT', uri=uri, data=document)

    def patch(self, kind, collection, key, document):
        uri = '{}/{}/{}/'.format(kind, collection, key)
        return self.make_request(method='PATCH', uri=uri, data=document)

    def delete(self, kind, collection, key):
        uri = '{}/{}/{}/'.format(kind, collection, key)
        return self.make_request(method='DELETE', uri=uri)

    def clear(self, kind, collection, document):
        uri = '{}/{}/clear/'.format(kind, collection)
        return self.make_request(method='POST', uri=uri, data=document)
