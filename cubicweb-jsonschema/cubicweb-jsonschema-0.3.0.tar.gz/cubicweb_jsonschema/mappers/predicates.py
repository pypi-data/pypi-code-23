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
"""Predicates for Yams to JSON Schema mappers."""

from six import string_types

from logilab.common.registry import (
    Predicate,
    objectify_predicate,
)

from cubicweb.predicates import (
    ExpectedValuePredicate,
    PartialPredicateMixIn,
)


__all__ = [
    'yams_final_rtype',
    'yams_component_target',
    'yams_match',
    'partial_yams_match',
]


def _etype_from_context(kwargs):
    etype = kwargs.get('etype')
    if etype is None:
        entity = kwargs.get('entity')
        if entity is not None:
            etype = entity.cw_etype
    return etype


@objectify_predicate
def yams_final_rtype(cls, cnx, rtype=None, role=None, **kwargs):
    """Predicate that returns 1 when the supplied `rtype` is not final."""
    if rtype is None or role is None:
        return 0
    etype = _etype_from_context(kwargs)
    if etype is None:
        return 0
    rdef = cnx.vreg.schema[etype].rdef(rtype, role=role, takefirst=True)
    if rdef.final:
        return 1
    return 0


@objectify_predicate
def yams_component_target(cls, cnx, rtype=None, role=None, target_types=None,
                          **kwargs):
    """Predicate that returns 1 when the target entity types are component of
    the relation defined by `rtype` and `role` (i.e. the relation has
    composite set to `role`).
    """
    if rtype is None or role is None:
        return 0
    etype = _etype_from_context(kwargs)
    if etype is None:
        return 0
    component = None
    eschema = cnx.vreg.schema[etype]
    if target_types is None:
        rschema = cnx.vreg.schema[rtype]
        target_types = tuple(t.type for t in rschema.targets(etype, role=role))
    for target_type in target_types:
        rdef = eschema.rdef(rtype, role=role, targettype=target_type)
        _component = rdef.composite == role
        if component is None:
            component = _component
        elif not component == _component:
            cls.warning('component inconsistency accross target types')
            return 0
    return component


class yams_match(Predicate):
    """Predicate that returns a positive value when the supplied relation
    match parameters given as predicate argument.

    The more __call__ arguments match __init__'s ones, the higher the score
    is.
    """

    def __init__(self, etype=None, rtype=None, role=None, target_types=()):
        self.etype = etype
        self.rtype = rtype
        self.role = role
        if isinstance(target_types, string_types):
            target_types = {target_types}
        elif not isinstance(target_types, (set, frozenset)):
            target_types = frozenset(target_types)
        self.target_types = target_types

    def __call__(self, cls, cnx, rtype, role, **kwargs):
        etype = _etype_from_context(kwargs)
        score = 0
        for key in ('etype', 'rtype', 'role'):
            expected = getattr(self, key, None)
            if expected is not None:
                if locals()[key] != expected:
                    return 0
                score += 1
        target_types = kwargs.get('target_types', frozenset())
        assert isinstance(target_types, (set, frozenset)), \
            'yams_match must be called with a set as "target_types" argument'
        if self.target_types:
            if not target_types.issubset(self.target_types):
                return 0
            score += 1
        return score


class partial_yams_match(PartialPredicateMixIn, ExpectedValuePredicate):
    """Return non-zero if selected class's attributes `etype`, `rtype`, `role`
    and/or `target_types` match with keyword arguments from context.
    """

    match_attributes = ('etype', 'rtype', 'role', 'target_types')

    def __init__(self, *expected, **kwargs):
        super(partial_yams_match, self).__init__((), **kwargs)

    def complete(self, cls):
        self.expected = {}
        for name in self.match_attributes:
            if hasattr(cls, name):
                self.expected[name] = set([getattr(cls, name)])

    def _values_set(self, cls, req, **kwargs):
        values = {}
        for name in self.match_attributes:
            if name in kwargs:
                values[name] = kwargs[name]
        return values
