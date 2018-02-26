# coding: utf-8
# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

import sys
from io import BytesIO, StringIO

from cubicweb.devtools import (
    PostgresApptestConfiguration,
    testlib,
)
from cubicweb.cwconfig import CubicWebConfiguration

from cubicweb_eac import ccplugin
from cubicweb_skos import ccplugin as skos

import testutils


def setUpModule():
    testutils.startpgcluster(__file__)


class CCPluginTC(testlib.CubicWebTC):

    def setup_database(self):
        super(CCPluginTC, self).setup_database()
        self.orig_config_for = CubicWebConfiguration.config_for
        CubicWebConfiguration.config_for = staticmethod(lambda appid: self.config)

    def tearDown(self):
        CubicWebConfiguration.config_for = self.orig_config_for
        super(CCPluginTC, self).tearDown()


class ImportEacDataCommandTC(CCPluginTC):
    configcls = PostgresApptestConfiguration

    def setup_database(self):
        super(ImportEacDataCommandTC, self).setup_database()
        with self.admin_access.client_cnx() as cnx:
            testutils.authority_with_naa(cnx)  # ensure we have a naming authority
            cnx.commit()

    def run_import_eac(self, *args):
        cmd = [self.appid, self.datapath('D33-100.xml')] + list(args)
        sys.stdout = output = BytesIO()
        try:
            ccplugin.ImportEacData(None).main_run(cmd)
        except SystemExit as exc:
            code = exc.code
        else:
            code = 0
        finally:
            sys.stdout = sys.__stdout__
        return code, output.getvalue()

    def test_ok(self):
        code, output = self.run_import_eac()
        self.assertEqual(code, 0)
        with self.admin_access.repo_cnx() as cnx:
            record = cnx.find('AuthorityRecord').one()
            self.assertEqual(record.dc_title(), u"Centre d'information et d'orientation (CIO)")
            self.assertTrue(testutils.match_ark(record.ark), record.ark)

    def test_bad_authority(self):
        code, output = self.run_import_eac('--authority', 'unexisting')
        self.assertEqual(code, 1)
        self.assertIn('no authority named "unexisting"', output)

    def test_too_many_autorities(self):
        with self.admin_access.client_cnx() as cnx:
            testutils.authority_with_naa(cnx, name=u'hop')
            cnx.commit()
        code, output = self.run_import_eac()
        self.assertEqual(code, 1)
        self.assertIn('there are several authorities', output)

    def test_autority_has_no_naa(self):
        with self.admin_access.client_cnx() as cnx:
            org = testutils.authority_with_naa(cnx)
            org.cw_set(ark_naa=None)
            cnx.commit()
        code, output = self.run_import_eac()
        self.assertEqual(code, 1)
        self.assertIn('not associated to a ARK naming authority', output)


class ImportSkosDataCommandTC(CCPluginTC):

    configcls = PostgresApptestConfiguration

    def run_import_skos(self, *args):
        cmd = [self.appid] + list(args)
        sys.stdout = output = StringIO()
        try:
            skos.ImportSkosData(None).main_run(cmd)
        except SystemExit as exc:
            code = exc.code
        else:
            code = 0
        finally:
            sys.stdout = sys.__stdout__
        return code, output.getvalue()

    def test_lcsv(self):
        with self.admin_access.cnx() as cnx:
            naa = testutils.naa(cnx)
            scheme = cnx.create_entity('ConceptScheme', title=u'lcsv',
                                       ark_naa=naa)
            cnx.commit()
            scheme_uri = scheme.cwuri
            assert scheme.ark_naa
            assert scheme.ark
        code, output = self.run_import_skos(
            self.datapath('lcsv_example_shortened.csv'),
            '--format', 'lcsv',
            '--scheme', scheme.ark,
        )
        self.assertEqual(code, 0, output)
        with self.admin_access.cnx() as cnx:
            scheme = cnx.find('ConceptScheme', cwuri=scheme_uri).one()
            self.assertEqual(len(scheme.reverse_in_scheme), 3)

    def test_lcsv_missing_naa_what(self):
        with self.admin_access.cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'lcsv',
                                       ark=u'0/123', cwuri=u'123')
            cnx.commit()
            assert not scheme.ark_naa
        code, output = self.run_import_skos(
            self.datapath('lcsv_example_shortened.csv'),
            '--format', 'lcsv',
            '--scheme', '0/123',
        )
        self.assertEqual(code, 1, output)
        self.assertIn('command failed: specified concept scheme', output)


if __name__ == '__main__':
    from unittest import main
    main()
