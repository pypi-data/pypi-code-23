# coding: utf-8
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
"""cubicweb-saem-ref site customizations"""

import pytz

from logilab.common.date import ustrftime
from logilab.common.decorators import monkeypatch

from cubicweb import (
    NoResultError,
    cwvreg,
    _,
)
from cubicweb.cwconfig import register_persistent_options
from cubicweb.uilib import PRINTERS
from cubicweb.entity import Entity
from cubicweb.web import request

from cubicweb_skos import rdfio
from cubicweb_skos.ccplugin import ImportSkosData
import cubicweb_seda as seda
import cubicweb_seda.dataimport as seda_dataimport

from . import permanent_url, _massive_store_factory, _nohook_store_factory

# this import is needed to take account of pg_trgm monkeypatches
# while executing cubicweb-ctl commands (db-rebuild-fti)
from . import pg_trgm  # noqa pylint: disable=unused-import


# override Entity.rest_path to use ark for entities which have one

_orig_rest_path = Entity.rest_path


@monkeypatch(Entity)
def rest_path(self, *args, **kwargs):
    """Return ark:/<ARK> is entity has an ark attribute."""
    if getattr(self, 'ark', None) is None:
        return _orig_rest_path(self, *args, **kwargs)
    return u'ark:/' + self.ark


# configure RDF generator to use ark based uri as canonical uris, and deactivating implicit
# 'same_as_urls' in this case

orig_same_as_uris = rdfio.RDFGraphGenerator.same_as_uris


@monkeypatch(rdfio.RDFGraphGenerator, methodname='same_as_uris')
@staticmethod
def same_as_uris(entity):
    if entity.cwuri.startswith('ark:'):
        return ()
    return orig_same_as_uris(entity)


@monkeypatch(rdfio.RDFGraphGenerator, methodname='canonical_uri')
@staticmethod
def canonical_uri(entity):
    return permanent_url(entity)


# deactivate date-format and datetime-format cw properties. This is because we do some advanced date
# manipulation such as allowing partial date and this is not generic enough to allow arbitrary
# setting of date and time formats

base_user_property_keys = cwvreg.CWRegistryStore.user_property_keys


@monkeypatch(cwvreg.CWRegistryStore)
def user_property_keys(self, withsitewide=False):
    props = base_user_property_keys(self, withsitewide)
    return [prop for prop in props if prop not in ('ui.date-format', 'ui.datetime-format')]


# customize display of TZDatetime

register_persistent_options((
    ('timezone',
     {'type': 'choice',
      'choices': pytz.common_timezones,
      'default': 'Europe/Paris',
      'help': _('timezone in which time should be displayed'),
      'group': 'ui', 'sitewide': True,
      }),
))


def print_tzdatetime_local(value, req, *args, **kwargs):
    tz = pytz.timezone(req.property_value('ui.timezone'))
    value = value.replace(tzinfo=pytz.utc).astimezone(tz)
    return ustrftime(value, req.property_value('ui.datetime-format'))


PRINTERS['TZDatetime'] = print_tzdatetime_local


# configure c-c skos-import command's factories to use with proper metadata generator ##############

ImportSkosData.cw_store_factories['massive'] = _massive_store_factory
ImportSkosData.cw_store_factories['nohook'] = _nohook_store_factory


# override seda's scheme initialization to set ark on each scheme, and to use an ark enabled store

@monkeypatch(seda_dataimport)
def init_seda_scheme(cnx, title, _count=[]):
    description = u'edition 2009' if title.startswith('SEDA :') else None
    try:
        ark_naa = cnx.find('ArkNameAssigningAuthority', what=25651).one()
    except NoResultError:
        ark_naa = cnx.create_entity(
            'ArkNameAssigningAuthority', who=u'ADGIRONDE', what=25651)
    return cnx.create_entity('ConceptScheme', title=title, description=description,
                             ark_naa=ark_naa)


@monkeypatch(seda_dataimport)
def get_store(cnx):
    from .sobjects import SAEMMetadataGenerator
    metagen = SAEMMetadataGenerator(cnx, naa_what='25651')
    if cnx.repo.system_source.dbdriver == 'postgres':
        from cubicweb.dataimport.massive_store import MassiveObjectStore
        return MassiveObjectStore(cnx, metagen=metagen, eids_seq_range=1000)
    else:
        from cubicweb.dataimport.stores import NoHookRQLObjectStore
        return NoHookRQLObjectStore(cnx, metagen=metagen)


# configure seda compound graph to discard Activity and its relations, else it
# causes problem because it belongs to several graphs with different compound
# implementation (using "container" relation or not)
seda.GRAPH_SKIP_ETYPES.add('Activity')
# also, the new_version_of relation should not be considered as part of the
# graph (as for e.g. container or clone_of)
for rtype in ('new_version_of', 'use_profile'):
    seda.GRAPH_SKIP_RTYPES.add(rtype)
    Entity.cw_skip_copy_for.append((rtype, 'subject'))
    Entity.cw_skip_copy_for.append((rtype, 'object'))


@monkeypatch(request._CubicWebRequestBase)
def negotiated_language(self):
    # Force language to fr since in http-negociation mode there is no way to
    # force french language with a browser configured in english.
    # This is currently the easiest way to force the language of an instance.
    return 'fr'
