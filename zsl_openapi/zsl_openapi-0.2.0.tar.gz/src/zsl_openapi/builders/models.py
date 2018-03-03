from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import *  # NOQA
from inspect import isclass

from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.base import MANYTOONE
from sqlalchemy.orm.dependency import ManyToManyDP
from sqlalchemy.orm.dependency import ManyToOneDP
from sqlalchemy.orm.dependency import OneToManyDP
from sqlalchemy.orm.relationships import RelationshipProperty
from zsl.db.model.sql_alchemy import DeclarativeBase
from zsl.utils.string_helper import camelcase_to_underscore

from zsl_openapi.api import ApiDescription  # NOQA
from zsl_openapi.api import ApiModelDefinition  # NOQA
from zsl_openapi.api import ApiModelProperty  # NOQA
from zsl_openapi.builders import ApiDescriptionBuilder


class PersistentModelsApiDescriptionBuilder(ApiDescriptionBuilder):
    """Builds the ApiDescription for the persistent models. It is able to handle simple scalar properties and
    relationships.
    """

    def __init__(self, package):
        self._models = []
        self._append_models(package)

    def _append_models(self, package):
        for model in package.__dict__.values():
            if not isclass(model):
                continue

            if not issubclass(model, DeclarativeBase):
                continue

            if model == DeclarativeBase:
                continue

            self._models.append(model)

    def build(self, api_description):
        # type: (ApiDescription)->None
        for model in self._models:
            model_definition = self._generate_openapi_from_model(model)
            api_description.add_model_definition(model_definition)

    def _generate_openapi_from_model(self, model):
        # type: (DeclarativeBase)->ApiModelDefinition
        model_definition = ApiModelDefinition()
        model_definition.name = model.__name__
        model_definition.type = "object"

        for column_name in model.__dict__:
            column = getattr(model, column_name)
            if not isinstance(column, InstrumentedAttribute):
                continue

            self._extract_property(column, column_name, model_definition)

        return model_definition

    def _extract_property(self, column, column_name, model_definition):
        property_definition = ApiModelProperty()
        property_definition.name = column_name
        if isinstance(column.prop, RelationshipProperty):
            self._extract_relationship_property(column, property_definition)
        else:
            self._extract_scalar_property(column, property_definition)
        model_definition.add_property(property_definition)

    def _extract_relationship_property(self, column, property_definition):
        dp = self._get_dependency_processor(column)
        is_dp_supported = isinstance(dp, (ManyToManyDP, ManyToOneDP, OneToManyDP))
        if is_dp_supported:
            is_simple_object = column.prop._dependency_processor.direction == MANYTOONE
            if is_simple_object:
                property_definition.type = self._get_column_type(column)
            else:
                property_definition.type = "array"
                property_definition.items.ref = "#/definitions/{0}".format(self._get_column_type(column))
        else:
            raise TypeError("Can not process type definitions, dependency processor {0} is not supported.".format(dp))

    def _get_column_type(self, column):
        return column.prop.mapper.class_.__name__

    def _get_dependency_processor(self, column):
        return column.prop._dependency_processor if column.prop._dependency_processor else \
            column.property._dependency_processor

    def _extract_scalar_property(self, column, property_definition):
        property_type = camelcase_to_underscore(type(column.type).__name__)
        property_format = None
        if property_type == "date_time":
            property_type = "string"
            property_format = "date-time"

        property_definition.type = property_type
        property_definition.format = property_format
