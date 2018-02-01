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
"""JSON Schema mappers for workflows-related entity types."""

from logilab.common.registry import (
    objectify_predicate,
)
from cubicweb.predicates import (
    match_kwargs,
)

from .. import (
    CREATION_ROLE,
)
from .base import (
    add_descriptive_metadata,
    add_links,
)
from .entities import (
    EntityCollectionMapper,
    ETypeMapper,
)


@objectify_predicate
def _for_workflowable_entity(cls, cnx, for_entity=None, **kwargs):
    """Return 1 if `for_entity` context argument corresponds to a worflowable
    entity type.
    """
    if for_entity is not None:
        wfobj = for_entity.cw_adapt_to('IWorkflowable')
        if wfobj is not None:
            return 1
    return 0


class TrInfoEntityMapper(ETypeMapper):
    """Mapper for TrInfo entity types associated with an entity."""
    __select__ = (
        match_kwargs({'etype': 'TrInfo'})
        & _for_workflowable_entity()
    )

    @add_links
    def schema_and_definitions(self, schema_role=None):
        # For creation role, we return a custom schema (which is quite
        # unrelated to Yams schema) so that the end user sees a document with
        # the name of the transition (and a comment) instead of getting
        # exposed to the implementation details of CubicWeb workflows data
        # model.
        if schema_role != CREATION_ROLE:
            return super(TrInfoEntityMapper, self).schema_and_definitions(
                schema_role=schema_role)
        entity = self.cw_extra_kwargs['for_entity']
        wfobj = entity.cw_adapt_to('IWorkflowable')
        _ = self._cw._
        transitions_choice = [{'enum': [tr.name], 'title': _(tr.name)}
                              for tr in wfobj.possible_transitions()]
        schema = {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'oneOf': transitions_choice,
                },
                'comment': {
                    'type': 'string'
                },
            },
            'required': ['name'],
        }
        return add_descriptive_metadata(schema, self), None


class TrInfoCollectionMapper(EntityCollectionMapper):
    """Mapper for a collection of TrInfo associated with an entity."""
    __select__ = (
        match_kwargs({'etype': 'TrInfo'})
        & _for_workflowable_entity()
    )

    def values(self, *args):
        # This is handled by the view.
        raise NotImplementedError()

    def serialize(self):
        entity = self.cw_extra_kwargs['for_entity']
        wfobj = entity.cw_adapt_to('IWorkflowable')
        entities = wfobj.workflow_history
        return super(TrInfoCollectionMapper, self).serialize(entities)
