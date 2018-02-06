"""This module is in charge of building a Aug object from it's over the wire form.

Since most serialization format do not support polymorphism, we add this capability in this module.

This module finds and loads all dynamic classes and dynamically builds the relevant component based on it's id.
"""

import six

from rook.lib.factory import Factory

from ..augs import actions, conditions, extractors, locations
from ..augs.aug import Aug

from .processor_extensions.operations.celery_rdb import CeleryRdb, CeleryRdbGetPort

from rook.lib.logger import logger
from rook.lib.rookout_json import json

from rook.lib.processor.processor_factory import ProcessorFactory

from rook.exceptions import ToolException, RookAugInvalidKey, RookObjectNameMissing, RookUnknownObject, RookInvalidObjectConfiguration


class AugFactory(Factory):
    """This is the factory for building Augs by their configuration."""

    def __init__(self, output):
        """Initialize the class."""
        super(AugFactory, self).__init__()

        self._output = output
        self._processor_factory = ProcessorFactory([CeleryRdb, CeleryRdbGetPort], [])

        self._load_dynamic_classes()

    def get_aug(self, configuration):
        """Returns an Aug object based on the given configuration."""
        try:
            aug_id = configuration['id']
        except KeyError as exc:
            six.raise_from(RookAugInvalidKey('id', json.dumps(configuration)), exc)

        try:
            locationDict = configuration['location']
        except KeyError as exc:
            six.raise_from(RookAugInvalidKey('location', json.dumps(configuration)), exc)
        location = self._get_dynamic_class(locationDict)

        if 'extractor' in configuration:
            extractor = self._get_dynamic_class(configuration['extractor'])
        else :
            extractor = None

        if 'condition' in configuration:
            condition = self._get_dynamic_class(configuration['condition'])
        else :
            condition = None

        try:
            actionDict = configuration['action']
        except KeyError as exc:
            six.raise_from(RookAugInvalidKey('action', json.dumps(configuration)), exc)
        action = self._get_dynamic_class(actionDict)

        return Aug(aug_id, location, extractor, condition, action, self._output)

    def _load_dynamic_classes(self):
        """Load all dynamic classes into the factory."""
        self.register_methods(locations.__all__)
        self.register_methods(extractors.__all__)
        self.register_methods(conditions.__all__)
        self.register_methods(actions.__all__)

    def _get_dynamic_class(self, configuration):
        """Return a class based on configuration."""

        if not configuration:
            return None
        else:
            try:
                name = configuration['name']
            except KeyError as exc:
                six.raise_from(RookObjectNameMissing(json.dumps(configuration)), exc)

            try:
                factory = self.get_object_factory(name)
            except (AttributeError, KeyError) as exc:
                six.raise_from(RookUnknownObject(name), exc)

            try:
                return factory(configuration, self._processor_factory)
            except ToolException:
                raise
            except Exception as exc:
                six.raise_from(RookInvalidObjectConfiguration(name, json.dumps(configuration)), exc)
