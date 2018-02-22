# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from cubicweb.devtools import PostgresApptestConfiguration
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_saem_ref.ark import (
    ARK_QUALIFIER_LENGTH,
)
import testutils


def setUpModule():
    testutils.startpgcluster(__file__)


class ArkGeneratorTC(CubicWebTC):

    configcls = PostgresApptestConfiguration

    def test(self):
        what = '31400'
        with self.admin_access.repo_cnx() as cnx:
            generator = self.vreg['adapters'].select(
                'IARKGenerator', cnx, naa_what=what)
            ark = generator.generate_ark()
        self.assertTrue(ark.startswith(what + '/'), ark)
        name = ark[len(what) + 1:]
        self.assertTrue(testutils.match_ark_name(name), name)

    def _check_ark_matches_parent(self, ark, parent_ark):
        self.assertTrue(ark.startswith(parent_ark + '/'), ark)
        qualifier = ark[len(parent_ark) + 1:]
        self.assertEqual(len(qualifier), ARK_QUALIFIER_LENGTH)

    def test_concept(self):
        with self.admin_access.cnx() as cnx:
            scheme = testutils.setup_scheme(cnx, u'test')
            cnx.commit()
            scheme_ark = scheme.ark
            what = str(scheme.ark_naa[0].what)
            generator = self.vreg['adapters'].select(
                'IARKGenerator', cnx, naa_what=what, in_scheme=scheme)
            ark = generator.generate_ark()
            self._check_ark_matches_parent(ark, scheme_ark)

    def test_organizationunit(self):
        with self.admin_access.cnx() as cnx:
            authority = testutils.authority_with_naa(cnx)
            cnx.commit()
            authority_ark = authority.ark
            what = str(authority.ark_naa[0].what)
            generator = self.vreg['adapters'].select(
                'IARKGenerator', cnx, naa_what=what, authority=authority)
            ark = generator.generate_ark()
            self._check_ark_matches_parent(ark, authority_ark)


if __name__ == '__main__':
    import unittest
    unittest.main()
