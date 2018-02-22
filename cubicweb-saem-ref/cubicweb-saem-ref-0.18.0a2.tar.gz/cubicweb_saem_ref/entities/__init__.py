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
"""cubicweb-saem-ref entity's classes"""

from logilab.common.decorators import monkeypatch

from cubicweb.view import Adapter, EntityAdapter
from cubicweb.predicates import match_kwargs, relation_possible, is_instance
from cubicweb.entities import AnyEntity, fetch_config, authobjs, lib

from .. import ark


class ARKIdentifierGeneratorMixin(object):
    __regid__ = 'IARKGenerator'
    __select__ = match_kwargs('naa_what')

    def generate_ark(self):
        """Return a new ARK identifier as unicode"""
        return u'{0}/{1}'.format(self.cw_extra_kwargs['naa_what'], self.assign_name())


class ARKIdentifierGenerator(ARKIdentifierGeneratorMixin, Adapter):
    """Adapter for ARK unique identifier generation"""

    def assign_name(self):
        """Assign and return a new name part of the ARK identifier"""
        naan = int(self.cw_extra_kwargs['naa_what'])
        return ark.generate_ark(self._cw, naan)


class QualifiedARKIdentifierGenerator(ARKIdentifierGeneratorMixin, Adapter):
    """Adapter for ARK identifier generation using a qualifier from an
    existing "base" ARK identifier.
    """
    __abstract__ = True

    @property
    def parent_entity(self):
        raise NotImplementedError

    def assign_name(self):
        match = ark.match(self.parent_entity.ark)
        if not match:
            raise ValueError(
                "ARK identifier for parent entity #%d looks malformattted: %s"
                % (self.parent_entity.eid, self.parent_entity.ark)
            )
        naan = int(self.cw_extra_kwargs['naa_what'])
        # Sanity check to make sure we're not producing ARK identifiers with
        # different NAAN for entities that are supposed to be parent of each
        # others.
        if int(match.group('naan')) != naan:
            raise ValueError(
                "NAAN of parent entity ark:/%s does not match the value of "
                "'naa_what' parameter: %s"
                % (self.parent_entity.ark, naan)
            )
        name = match.group('name')
        qualifier = ark.generate_qualified_ark(self._cw, naan, name)
        return u'/'.join([name, qualifier])


class ConceptARKIdentifierGenerator(QualifiedARKIdentifierGenerator):
    __select__ = (
        ARKIdentifierGeneratorMixin.__select__
        & match_kwargs('in_scheme')
    )

    @property
    def parent_entity(self):
        scheme = self.cw_extra_kwargs['in_scheme']
        if hasattr(scheme, 'eid'):
            return scheme
        return self._cw.entity_from_eid(scheme)


class OUARKIdentifierGenerator(QualifiedARKIdentifierGenerator):
    __select__ = (
        ARKIdentifierGeneratorMixin.__select__
        & match_kwargs('authority')
    )

    @property
    def parent_entity(self):
        authority = self.cw_extra_kwargs['authority']
        if hasattr(authority, 'eid'):
            return authority
        return self._cw.entity_from_eid(authority)


class ArkNAALocator(EntityAdapter):
    """Adapter responsible to retrieve the proper ARK Name Assigning Authority depending on the
    entity type
    """
    __abstract__ = True
    __regid__ = 'IArkNAALocator'

    def naa_what(self):
        """Return the ARK NameAssigningAuthority entity or None if not specified"""
        raise NotImplementedError()


class DirectArkNAALocator(ArkNAALocator):
    """Return NAA specified through the ark_naa relation"""
    __select__ = relation_possible('ark_naa')

    def naa_what(self):
        # entity is usually not yet created, since ark has to be generated before entity creation
        if 'ark_naa' in getattr(self.entity, 'cw_edited', {}):
            return self._cw.entity_from_eid(self.entity.cw_edited['ark_naa']).what
        elif self.entity.ark_naa:
            return self.entity.ark_naa[0].what
        return None


class AgentArkNAALocator(ArkNAALocator):
    """Return NAA specified through the authority to which the agent belong"""
    __select__ = is_instance('Agent', 'OrganizationUnit')

    def naa_what(self):
        # entity is usually not yet created, since ark has to be generated before entity creation
        if 'authority' in getattr(self.entity, 'cw_edited', {}):
            authority = self._cw.entity_from_eid(self.entity.cw_edited['authority'])
            if authority.ark_naa:
                return authority.ark_naa[0].what
        elif self.entity.authority and self.authority[0].ark_naa:
            return self.authority[0].ark_naa[0].what
        return None


class ConceptArkNAALocator(ArkNAALocator):
    """Return NAA for Concept, through the concept scheme which it belongs to."""
    __select__ = is_instance('Concept')

    def naa_what(self):
        # entity is usually not yet created, since ark has to be generated before entity creation
        if 'in_scheme' in getattr(self.entity, 'cw_edited', {}):
            scheme = self._cw.entity_from_eid(self.entity.cw_edited['in_scheme'])
        elif self.entity.in_scheme:
            scheme = self.entity.in_scheme[0]
        else:
            return None
        return scheme.cw_adapt_to(self.__regid__).naa_what()


class ExternalUri(AnyEntity):
    __regid__ = 'ExternalUri'
    fetch_attrs, cw_fetch_order = fetch_config(('uri',))


class EmailAddress(lib.EmailAddress):
    fetch_attrs, cw_fetch_order = fetch_config(['address'])

    def dc_title(self):
        return self.display_address()


@monkeypatch(authobjs.CWUser, methodname='naa')
@property
def naa(self):
    if self.authority and self.authority[0].ark_naa:
        return self.authority[0].ark_naa[0]
    return None
