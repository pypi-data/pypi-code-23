# -*- coding: utf-8 -*-
from contacthub.models.query.entity_field import EntityField


class EntityMeta(type):
    """
    Metaclass for Properties class.
    Use this metaclass to handling the __getattr__ method and returns a new EntityField.
    This metaclass is useful for creating query objects and optimize the querying syntax.
    """

    def __getattr__(self, item):
        """
        If you call properties.field, this function create a new EntityField object with an entity and the requested
        item

        :param item: the properties that we want to query
        :return: a new EntityField object for queries
        """
        return EntityField(self, item)
