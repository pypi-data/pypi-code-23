# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-jsonschema resources tests"""

import unittest

from mock import (
    NonCallableMock,
    patch,
)

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb_jsonschema import resources


class ResourcesTC(unittest.TestCase):

    def tearDown(self):
        for cls in (resources.RootResource, resources.ETypeResource):
            cls._child_resources.clear()

    def test_metaclass(self):
        self.assertIsNot(resources.RootResource._child_resources,
                         resources.ETypeResource._child_resources)

    def test_pluggable_resource(self):

        @resources.RootResource.child_resource
        class SubResource(resources.TraversalResource):
            segment = 'segment'
            match = staticmethod(lambda r: True)

        request = object()
        resource = resources.RootResource(request)
        child_resource = resource['segment']
        self.assertIsInstance(child_resource, SubResource)
        self.assertIs(child_resource.__parent__, resource)
        self.assertIs(child_resource.request, request)

        # we've to patch resources.ETypeResource.__init__ else it will attempt
        # to access request.registry which is not set here (it would ends up
        # with a key error anyway)
        with patch.object(resources.ETypeResource, '__init__',
                          side_effect=KeyError):
            self.assertRaises(KeyError,
                              resource.__getitem__, 'unknown-segment')

    def test_multiple_matches_error(self):

        @resources.RootResource.child_resource
        class SubResource1(resources.TraversalResource):
            segment = 'segment'
            match = staticmethod(lambda r: True)

        @resources.RootResource.child_resource
        class SubResource2(resources.TraversalResource):
            segment = 'segment'
            match = staticmethod(lambda r: True)

        resource = resources.RootResource(None)
        with self.assertRaises(ValueError) as cm:
            resource.matching_resource('segment')

        self.assertIn('SubResource1', str(cm.exception))
        self.assertIn('SubResource2', str(cm.exception))


class WorkflowTransitionsResourceTC(CubicWebTC):

    def fake_request(self, cnx):
        registry = {'cubicweb.registry': self.vreg}
        return NonCallableMock(cw_cnx=cnx, params={},
                               registry=registry)

    def test_plugged_for_workflowable_entity(self):
        with self.admin_access.cnx() as cnx:
            root = resources.RootResource(self.fake_request(cnx))
            entity_resource = root['cwuser']['admin']
            try:
                entity_resource['workflow-transitions']
            except KeyError as e:
                self.fail(e)

    def test_not_plugged_for_non_workflowable_entity(self):
        with self.admin_access.cnx() as cnx:
            root = resources.RootResource(self.fake_request(cnx))
            entity_resource = root['cwgroup']['users']
            with self.assertRaises(KeyError):
                entity_resource['workflow-transitions']


if __name__ == '__main__':
    unittest.main()
