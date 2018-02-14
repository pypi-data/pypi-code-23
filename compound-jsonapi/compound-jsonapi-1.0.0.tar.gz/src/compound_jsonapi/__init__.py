"""
:mod:`compound_jsonapi`
=======================

The :mod:`compound_jsonapi` provides two main classes:

* The :class:`~compound_jsonapi.schema.Schema` acts as the base-class for all
  specific schemas that are then used to serialise / deserialise data. Details
  of its public interface can be found at :class:`~marshmallow.Schema`.
* The :class:`~compound_jsonapi.fields.Relationship` is a custom field to define
  relationships between :class:`~compound_jsonapi.schema.Schema`.

.. moduleauthor:: Mark Hall <mark.hall@work.room3b.eu>
"""
from .schema import Schema  # noqa:
from .fields import Relationship  # noqa:
