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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-eac schema"""

from yams.buildobjs import (EntityType, RelationDefinition, String, Date, Bytes,
                            RichString, ComputedRelation)
from yams.constraints import BoundaryConstraint, Attribute

from cubicweb import _
from cubicweb.schema import RRQLExpression, RQLVocabularyConstraint

from cubes.addressbook import schema as addressbook
from cubicweb_prov.schema import Activity


# Customization of addressbook schema.
for attrname in ('street', 'city', 'postalcode'):
    addressbook.PostalAddress.get_relation(attrname).cardinality = '?1'


def dated_entity_type(cls):
    """Class decorator adding `start_date` and `end_date` attribute to an
    EntityType.
    """
    cls.add_relation(Date(constraints=[BoundaryConstraint(
        '<=', Attribute('end_date'), msg=_('start date must be less than end date'))]),
        name='start_date')
    cls.add_relation(Date(), name='end_date')
    return cls


def xml_wrap(cls):
    """Class decorator adding an `xml_wrap` attribute to an EntityType."""
    desc = _('XML elements not contained in EAC-CPF namespace')
    cls.add_relation(Bytes(description=desc), name='xml_wrap')
    return cls


Activity.add_relation(String(description=_('the agent responsible for this activity'),
                             indexed=True, fulltextindexed=True), name='agent')


@dated_entity_type
class AuthorityRecord(EntityType):
    record_id = String(indexed=True)
    isni = String(unique=True,
                  description=_('International Standard Name Identifier'))


class NameEntry(EntityType):
    """Represent a nameEntry tag of an EAC-CPF document."""
    parts = String(
        required=True, fulltextindexed=True,
        description=_('concatenation of part tags within a nameEntry'))
    form_variant = String(internationalizable=True,
                          vocabulary=[_('authorized'), _('alternative')])


class name_entry_for(RelationDefinition):
    subject = 'NameEntry'
    object = 'AuthorityRecord'
    cardinality = '1+'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True


class EACOtherRecordId(EntityType):
    value = String(required=True, fulltextindexed=True, indexed=True)
    local_type = String(indexed=True)
    __unique_together__ = [('value', 'eac_other_record_id_of')]


class eac_other_record_id_of(RelationDefinition):
    subject = 'EACOtherRecordId'
    object = 'AuthorityRecord'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True


class AgentFunction(EntityType):
    """The function of an AuthorityRecord"""
    name = String(fulltextindexed=True, internationalizable=True)
    description = RichString(fulltextindexed=True)
    __unique_together__ = [('name', 'function_agent')]


class function_agent(RelationDefinition):
    subject = 'AgentFunction'
    object = 'AuthorityRecord'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True


class AgentPlace(EntityType):
    """Qualified relation between an AuthorityRecord and a PostalAddress"""
    name = String(fulltextindexed=True,
                  description=_('encoded information about the address (e.g. '
                                '"Paris, France")'))
    role = String(description=_('contextual role the address has in relation '
                                'with the agent (e.g. "home")'),
                  internationalizable=True)
    __unique_together__ = [('role', 'place_agent', 'place_address')]


class place_address(RelationDefinition):
    subject = 'AgentPlace'
    object = 'PostalAddress'
    cardinality = '?1'
    inlined = True
    composite = 'subject'
    fulltext_container = 'subject'


class place_agent(RelationDefinition):
    subject = 'AgentPlace'
    object = 'AuthorityRecord'
    cardinality = '1*'
    inlined = True
    composite = 'object'
    fulltext_container = 'object'


class postal_address(ComputedRelation):
    rule = 'P place_agent S, P place_address O'


class AgentKind(EntityType):
    """Kind of an authority record (e.g. "person", "authority" or "family")"""
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (),
        'update': (),
        'delete': (),
    }
    name = String(required=True, unique=True, internationalizable=True)


class agent_kind(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users'),
        'delete': (RRQLExpression('O name "unknown-agent-kind"'),),
    }
    subject = 'AuthorityRecord'
    object = 'AgentKind'
    cardinality = '1*'
    inlined = True


class GeneralContext(EntityType):
    """Information about the general social and cultural context of an authority record"""
    content = RichString(fulltextindexed=True)


class general_context_of(RelationDefinition):
    subject = 'GeneralContext'
    object = 'AuthorityRecord'
    cardinality = '1*'
    inlined = True
    composite = 'object'
    fulltext_container = 'object'


class _agent_relation(RelationDefinition):
    """Abstract relation between authority record"""
    subject = None
    object = ('AuthorityRecord', 'ExternalUri')
    cardinality = '1*'
    inlined = True


@xml_wrap
@dated_entity_type
class AssociationRelation(EntityType):
    """Association relation between authority records"""
    entry = String()
    description = RichString()


class association_from(_agent_relation):
    subject = 'AssociationRelation'


class association_to(_agent_relation):
    subject = 'AssociationRelation'


@xml_wrap
@dated_entity_type
class ChronologicalRelation(EntityType):
    """Chronological relation between authority records"""
    entry = String()
    description = RichString()


class chronological_predecessor(_agent_relation):
    subject = 'ChronologicalRelation'


class chronological_successor(_agent_relation):
    subject = 'ChronologicalRelation'


@xml_wrap
@dated_entity_type
class HierarchicalRelation(EntityType):
    """Hierarchical relation between authority records"""
    entry = String()
    description = RichString()


class hierarchical_parent(_agent_relation):
    subject = 'HierarchicalRelation'


class hierarchical_child(_agent_relation):
    subject = 'HierarchicalRelation'


class generated(RelationDefinition):
    subject = 'Activity'
    object = 'AuthorityRecord'


class used(RelationDefinition):
    subject = 'Activity'
    object = 'AuthorityRecord'


@dated_entity_type
class Mandate(EntityType):
    """Reference text coming from an authority"""
    term = String(fulltextindexed=True)
    description = RichString(fulltextindexed=True)


@dated_entity_type
class LegalStatus(EntityType):
    """Information relative to the legal status of an authority"""
    term = String(fulltextindexed=True)
    description = RichString(fulltextindexed=True)


class History(EntityType):
    """Biographical or historical information"""
    text = RichString(fulltextindexed=True)


class Structure(EntityType):
    """Information about the structure of an authority"""
    description = RichString(fulltextindexed=True)


@dated_entity_type
class Occupation(EntityType):
    term = String(fulltextindexed=True)
    description = RichString(fulltextindexed=True)


class occupation_agent(RelationDefinition):
    subject = 'Occupation'
    object = 'AuthorityRecord'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True
    description = _('occupation in which the person works or has worked')


class mandate_agent(RelationDefinition):
    subject = 'Mandate'
    object = 'AuthorityRecord'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True
    description = _('mandate of an authority record')


class legal_status_agent(RelationDefinition):
    subject = 'LegalStatus'
    object = 'AuthorityRecord'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True
    description = _('legal status of an authority record')


class structure_agent(RelationDefinition):
    subject = 'Structure'
    object = 'AuthorityRecord'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True
    description = _('information about the structure of an authority record')


class history_agent(RelationDefinition):
    subject = 'History'
    object = 'AuthorityRecord'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True
    description = _('information about the history of an authority record')


class Citation(EntityType):
    note = RichString()
    uri = String()


class has_citation(RelationDefinition):
    subject = ('GeneralContext', 'Mandate', 'Occupation', 'History',
               'AgentFunction', 'LegalStatus', 'AgentPlace')
    object = 'Citation'
    cardinality = '*1'
    composite = 'subject'
    description = _('reference to an external citation resource')


@xml_wrap
@dated_entity_type
class EACResourceRelation(EntityType):
    """Represent a relation between an AuthorityRecord and a remote resource in the
    EAC-CPF model.
    """
    agent_role = String(description=_('type of relation the agent has to the resource'),
                        internationalizable=True)
    resource_role = String(description=_('type or nature of the remote resource'),
                           internationalizable=True)
    description = RichString(fulltextindexed=True)


class resource_relation_agent(RelationDefinition):
    subject = 'EACResourceRelation'
    object = 'AuthorityRecord'
    cardinality = '1*'
    inlined = True
    composite = 'object'
    fulltext_container = 'object'


class resource_relation_resource(RelationDefinition):
    subject = 'EACResourceRelation'
    object = 'ExternalUri'
    cardinality = '1*'
    inlined = True


@xml_wrap
class EACSource(EntityType):
    """A source used to establish the description of an AuthorityRecord"""
    title = String(fulltextindexed=True)
    url = String()
    description = RichString(fulltextindexed=True)


class source_agent(RelationDefinition):
    subject = 'EACSource'
    object = 'AuthorityRecord'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True


class vocabulary_source(RelationDefinition):
    subject = ('Mandate', 'LegalStatus', 'AgentFunction', 'AgentPlace',
               'Occupation')
    object = 'ConceptScheme'
    cardinality = '?*'


class equivalent_concept(RelationDefinition):
    subject = ('Mandate', 'LegalStatus', 'AgentFunction', 'AgentPlace',
               'Occupation')
    object = ('ExternalUri', 'Concept')
    constraints = [RQLVocabularyConstraint('S vocabulary_source SC, O in_scheme SC')]
    cardinality = '?*'
    # relation with 'ExternalUri' as object can't be inlined because of a limitation of
    # data-import's (massive) store
    inlined = False


def post_build_callback(schema):
    from cubicweb_eac import AuthorityRecordGraph
    from cubicweb_compound.utils import (graph_set_etypes_update_permissions,
                                         graph_set_write_rdefs_permissions)

    graph = AuthorityRecordGraph(schema)
    graph_set_etypes_update_permissions(schema, graph, 'AuthorityRecord')
    graph_set_write_rdefs_permissions(schema, graph, 'AuthorityRecord')
