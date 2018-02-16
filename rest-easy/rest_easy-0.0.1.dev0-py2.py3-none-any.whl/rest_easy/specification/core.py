# -*- coding: utf-8 -*-
"""Specifications for a ReST API.

Specifications are customized Marshmallow schemas.
"""

from marshmallow.schema import BaseSchema, SchemaMeta
from six import with_metaclass


class SpecificationMeta(SchemaMeta):
    pass


class SpecificationBase(BaseSchema):
    pass


class Specification(with_metaclass(SpecificationMeta, SpecificationBase)):
    pass
