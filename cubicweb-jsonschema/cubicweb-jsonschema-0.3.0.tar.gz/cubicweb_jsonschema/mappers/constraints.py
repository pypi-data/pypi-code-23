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
"""cubicweb-jsonschema mappers for Yams constraints."""

from logilab.common.registry import Predicate

from .. import (
    CREATION_ROLE,
    EDITION_ROLE,
)
from . import JSONSchemaMapper


class yams_constraint_type(Predicate):
    """ Predicate that returns 1 when the yams constraint supplied at execution
    time matches the constraint type name supplied at construction time (e.g.
    "SizeConstraint", "StaticVocabularyConstraint", etc.).
    """

    def __init__(self, cstr_type):
        self.cstr_type = cstr_type

    def __call__(self, cls, vreg, _, etype, rtype, cstr, **kwargs):
        if cstr.type() == self.cstr_type:
            return 1
        return 0


class ConstraintSerializer(JSONSchemaMapper):
    __regid__ = 'jsonschema.constraint'
    __abstract__ = True

    def __init__(self, vreg, _, etype, rtype, constraint):
        self.vreg = vreg
        self._ = _
        self.etype = vreg.schema[etype]
        self.rtype = vreg.schema[rtype]
        self.constraint = constraint


class SizeConstraintSerializer(ConstraintSerializer):
    __select__ = yams_constraint_type('SizeConstraint')

    def schema_and_definitions(self, schema_role=None):
        if schema_role not in (CREATION_ROLE, EDITION_ROLE):
            return {}, None
        if self.constraint.min is not None:
            return {'minLength': self.constraint.min}, None
        if self.constraint.max is not None:
            return {'maxLength': self.constraint.max}, None


class IntervalBoundConstraintSerializer(ConstraintSerializer):
    __select__ = yams_constraint_type('IntervalBoundConstraint')

    def schema_and_definitions(self, schema_role=None):
        if schema_role not in (CREATION_ROLE, EDITION_ROLE):
            return {}, None
        if self.constraint.minvalue is not None:
            return {'minimum': self.constraint.minvalue}, None
        if self.constraint.maxvalue is not None:
            return {'maximum': self.constraint.maxvalue}, None
