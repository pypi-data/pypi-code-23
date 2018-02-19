# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as publishged by the Free
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
"""cubicweb-saem-ref tests for SEDA cube integration"""

import re
import unittest

from six import text_type

from cubicweb.devtools import PostgresApptestConfiguration
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_seda.entities.profile_generation import SEDA1XSDExport, SEDA2RelaxNGExport

from cubicweb_saem_ref.entities import seda  # noqa - trigger monkey-patch

import testutils


def setUpModule():
    testutils.startpgcluster(__file__)


class CWURIURLTC(unittest.TestCase):

    def test(self):

        class FakeEntity(object):
            def __init__(self, cwuri):
                self.cwuri = cwuri
                self._cw = self

            def build_url(self, uri):
                return 'http://thistest/' + uri

        self.assertEqual(SEDA1XSDExport.cwuri_url(FakeEntity('ark:12/3')),
                         'http://thistest/ark:12/3')
        self.assertEqual(SEDA1XSDExport.cwuri_url(FakeEntity('http://othertest/ark:12/3')),
                         'http://othertest/ark:12/3')
        self.assertEqual(SEDA1XSDExport.cwuri_url(FakeEntity('http://othertest/whatever')),
                         'http://othertest/whatever')
        self.assertEqual(SEDA1XSDExport.cwuri_url(FakeEntity('whatever')),
                         'whatever')

        self.assertEqual(SEDA2RelaxNGExport.cwuri_url(FakeEntity('ark:12/3')),
                         'http://thistest/ark:12/3')
        self.assertEqual(SEDA2RelaxNGExport.cwuri_url(FakeEntity('http://othertest/ark:12/3')),
                         'http://othertest/ark:12/3')
        self.assertEqual(SEDA2RelaxNGExport.cwuri_url(FakeEntity('http://othertest/whatever')),
                         'http://othertest/whatever')
        self.assertEqual(SEDA2RelaxNGExport.cwuri_url(FakeEntity('whatever')),
                         'whatever')


class SEDAExportTC(CubicWebTC):

    configcls = PostgresApptestConfiguration

    def iter_seda_xsd(self, transfer):
        """Yield XSD representations of the transfer for SEDA 0.2 then 1.0,
        within a subTest.
        """
        for adapter_id in ('SEDA-0.2.xsd', 'SEDA-1.0.xsd'):
            with self.subTest(adapter=adapter_id):
                adapter = transfer.cw_adapt_to(adapter_id)
                yield adapter.dump()

    def test_include_profile_ark(self):
        with self.admin_access.client_cnx() as cnx:
            transfer = testutils.seda_transfer(cnx)
            testutils.create_archive_unit(transfer)
            cnx.commit()
            for xml in self.iter_seda_xsd(transfer):
                self.assertIn('ArchivalProfile', xml)
                self.assertIn('ark:/' + transfer.ark, xml)

    def test_include_agency_ark(self):
        with self.admin_access.client_cnx() as cnx:
            transfer = testutils.seda_transfer(cnx)
            _, _, unit_alt_seq = testutils.create_archive_unit(transfer)
            agency = cnx.create_entity('SEDAOriginatingAgency',
                                       seda_originating_agency_from=unit_alt_seq)

            # ensure it doesn't crash if agency is not tight to an authority record
            for xml in self.iter_seda_xsd(transfer):
                self.assertIn('OriginatingAgency', xml)

            # ensure we get the ark as agency identifier
            record = testutils.authority_record(cnx, u'DGSI')
            agency.cw_set(seda_originating_agency_to=record)
            for xml in self.iter_seda_xsd(transfer):
                self.assertIn('ark:/' + record.ark, xml)


class CloneImportTC(CubicWebTC):
    """Tests for cubicweb-seda's seda.doimport controller, making sure it
    works in SAEM-Ref as well.

    Copied and adapted eponymous class in cubicweb-seda/test/test_views.py.
    """

    configcls = PostgresApptestConfiguration

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            transfer = testutils.setup_profile(cnx, title=u'test')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx,
                                                                         user_cardinality=u'1',
                                                                         user_annotation=u'plop')
            self.transfer_eid = transfer.eid
            self.unit_eid = unit.eid
            cnx.commit()

    def test_import_one_entity(self):
        params = dict(eid=text_type(self.transfer_eid),
                      cloned=text_type(self.unit_eid))
        with self.admin_access.web_request(**params) as req:
            path, _ = self.expect_redirect_handle_request(
                req, 'seda.doimport')
            match = re.match(r'^ark:/(0/rf.{7}g)$', path)
            assert match, path
            ark = match.group(1)
            rset = req.execute('Any X WHERE X seda_archive_unit P, P ark %(ark)s',
                               {'ark': ark})
            self.assertTrue(rset)


if __name__ == '__main__':
    unittest.main()
