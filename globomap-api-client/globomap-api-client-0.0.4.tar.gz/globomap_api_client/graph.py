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


class Graph(Base):

    def post(self, document):
        return self.make_request(method='POST', uri='graphs', data=document)

    def list(self):
        return self.make_request(method='GET', uri='graphs')

    def traversal(self, graph, start_vertex, **kwargs):
        uri = 'graphs/{}/traversal/'.format(graph)
        params = {
            'start_vertex': start_vertex,
        }

        keys = ('item_order', 'strategy', 'order', 'edge_uniqueness',
                'vertex_uniqueness', 'max_iter', 'min_depth', 'max_depth',
                'init_func', 'sort_func', 'filter_func', 'visitor_func',
                'expander_func'
                )
        for kw in kwargs:
            if kw in keys:
                params[kw] = kwargs[kw]

        return self.make_request(method='GET', uri=uri, params=params)
