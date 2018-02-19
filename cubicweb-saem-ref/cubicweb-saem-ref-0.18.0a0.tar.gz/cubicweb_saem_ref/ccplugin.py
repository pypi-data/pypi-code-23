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
"""cubicweb-ctl plugin customizing data import commands."""
from __future__ import print_function

import sys

from six import PY2

from logilab.common.decorators import monkeypatch

from cubicweb import MultipleResultsError, NoResultError
from cubicweb.toolsutils import underline_title
from cubicweb.utils import admincnx

from cubicweb_skos import ccplugin as skos
from cubicweb_eac import ccplugin as eac

from . import _massive_store_factory, _nohook_store_factory


eac.ImportEacData.options = (
    ("authority", {
        'short': 'n', 'type': 'string',
        'default': False,
        'help': ('Name of the reference authority to use while importing data. This authority '
                 'should be linked to an NAA that will be used to attribute ARK identifiers. '
                 'If not specified, a single one is expected to be found in the database.'),
    }),
)


def _skos_drop_rql_store():
    """Remove "rql" store from ImportSkosData command.

    "rql" store is not supported in saem_ref because it cannot handle a
    metadata generator which is needed in saem_ref to generate ARK
    identifiers.
    """
    for name, value in skos.ImportSkosData.options:
        if name == 'cw-store':
            value['choices'] = tuple(c for c in value['choices'] if c != 'rql')
            assert 'nohook' in value['choices'], value['choices']
            value['default'] = 'nohook'
            break
    else:
        raise AssertionError(
            'Could not find "cw-store" option in ImportSkosData ccplugin command')
    del skos.ImportSkosData.cw_store_factories['rql']


_skos_drop_rql_store()
del _skos_drop_rql_store


def _skos_reword_scheme_option():
    """Change "--scheme" option help of skos-import command to match SAEM
    semantics (which relies on ARK instead of bare URI).
    """
    for name, value in skos.ImportSkosData.options:
        if name == 'scheme':
            value['help'] = (
                'ARK identifier of an existing concept scheme to import concepts in '
                '(only relevant for LCSV import format)'
            )
            break
    else:
        raise AssertionError(
            'Could not find "scheme" option in ImportSkosData ccplugin command')


_skos_reword_scheme_option()
del _skos_reword_scheme_option


def _enc(string):
    if PY2 and not isinstance(string, str):
        string = string.encode('utf-8')
    return string


@monkeypatch(eac.ImportEacData)
def run(self, args):
    appid = args[0]
    repo = None
    try:
        with admincnx(appid) as cnx:
            repo = cnx.repo
            org_name = self.config.authority
            if org_name:
                try:
                    org = cnx.find('Organization', name=org_name).one()
                except NoResultError:
                    print('ERROR: there are no authority named "{}"'.format(org_name))
                    sys.exit(1)
            else:
                org_rset = cnx.find('Organization')
                try:
                    org = org_rset.one()
                except MultipleResultsError:
                    print('ERROR: there are several authorities, choose the one to use using '
                          '--authority option. It should be one of {}'.format(
                              ', '.join(_enc(org.name) for org in org_rset.entities())))
                    sys.exit(1)
            if not org.ark_naa:
                print('ERROR: authority {} is not associated to a ARK naming authority. Choose '
                      'another organization or associate it to a ARK naming authority first.'
                      .format(_enc(org.name)))
                sys.exit(1)

            print('\n%s' % underline_title('Importing EAC files'))
            if cnx.repo.system_source.dbdriver == 'postgres':
                store = _massive_store_factory(cnx, self.config, eids_seq_range=100)
                store.metagen.naa_what = org.ark_naa[0].what
            else:
                store = _nohook_store_factory(cnx, self.config)
            eac.eac_import_files(cnx, args[1:], authority=org, store=store)
    finally:
        if repo is not None:
            repo.shutdown()


_orig_run = skos.ImportSkosData.run


@monkeypatch(skos.ImportSkosData)  # noqa: F811
def run(self, args):
    if self.get('format') == 'lcsv':
        scheme_ark = self.get('scheme')
        if not scheme_ark:
            print(u'command failed: --scheme option is required for LCSV import')
            sys.exit(1)
        scheme_ark = scheme_ark.strip().decode('utf-8')
        appid = args[0]
        connection = self.get_cnx(appid)
        try:
            with connection as cnx:
                if scheme_ark.startswith(u'ark:/'):
                    scheme_ark = scheme_ark[len(u'ark:/'):]
                rset = cnx.find('ConceptScheme', ark=scheme_ark)
                if not rset:
                    print(u'command failed: no concept scheme found matching "%s"'
                          % scheme_ark)
                    raise Exception
                scheme = rset.one()
                # cubicweb-skos's command need a cwuri for --scheme.
                setattr(self.config, 'scheme', scheme.cwuri)
                # Per schema, ark_naa is optional for ConceptScheme.
                if not scheme.ark_naa:
                    print(u'command failed: specified concept scheme "%s" must have an ARK NAA set'
                          % scheme_ark)
                    raise Exception
                naa_what = scheme.ark_naa[0].what
                print(u'Importing concepts in %s' % scheme.absolute_url())
        except Exception:
            connection.repo.shutdown()
            sys.exit(1)
        # Set a "config" attribute which will be retrieved from metadata
        # generator defined in __init__.py.
        setattr(self.config, 'naa_what', naa_what)
    return _orig_run(self, args)
