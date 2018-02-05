# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

from ..group import Group, GroupItem
from ..extensible import Extensible


class BlueprintItem(GroupItem, Extensible):

    def query_qe(self, queryexpr):

        got = self.api.post(self.url + "/qe", json={'query': queryexpr.strip()})
        if not got.ok:
            raise RuntimeError(
                'unable to execute query: %s' % got.reason,
                self, got)

        return got.json()['items']

    def query_ql(self, queryexpr, **queryvars):
        query = dict(query=queryexpr.strip())
        if queryvars:
            query['variables'] = queryvars

        got = self.api.post(self.url + "/ql", json=query)
        if not got.ok:
            raise RuntimeError(
                'unable to execute query: %s' % got.reason,
                self, got)

        return got.json()['data']


class Blueprints(Group):
    group_endpoint = '/api/blueprints'
    groupitem_class = BlueprintItem


def plugin(client):
    return Blueprints(client)
