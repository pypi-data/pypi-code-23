# -*- coding: utf-8 -*-

import collections
from .base import Scope, BaseDef
import logging
logger = logging.getLogger(__name__)


class Container(object):
    def __init__(self, config=None):
        self.config = config
        self.proxy_defines = {}
        self.proxy_objects = {}
        self.objects = {}
        self.defines = self.config.read_object_defines(self) if config is not None else collections.OrderedDict()

    def update(self, container):
        self.proxy_defines.update(container.proxy_defines)
        self.proxy_objects.update(container.proxy_objects)
        self.objects.update(container.objects)
        self.defines.update(container.defines)

    def get(self, name):
        obj = self.proxy_objects.get(name)
        if not obj:
            proxy_define = self.proxy_defines.get(name)
            if proxy_define:
                obj = self.create_object(proxy_define)
                define = self.defines.get(name)
                if define and define.scope == Scope.SINGLETON:
                    self.proxy_objects[name] = obj
            else:
                obj = self.get_object(name)
        return obj

    def get_object(self, name):
        try:
            return self.objects[name]
        except KeyError:
            logger.debug("Did NOT find object '%s' in the singleton storage." % name)
            try:
                define = self.defines[name]
            except KeyError as e:
                logger.error("Object '%s' has no definition!" % name)
                raise e
            else:
                comp = self.create_object(define)
                if define.scope == Scope.SINGLETON:
                    self.objects[name] = comp
                    logger.debug("Stored object '%s' in container's singleton storage" % name)
                return comp

    def create_object(self, define):
        logger.debug("Create object with define: %s", define)
        args = []
        for arg in define.args:
            if isinstance(arg, BaseDef):
                args.append(arg.get_actual_value(self))
            else:
                args.append(arg)

        kwargs = {}
        for k, v in define.kwargs.items():
            if isinstance(v, BaseDef):
                kwargs[k] = v.get_actual_value(self)
            else:
                kwargs[k] = v

        obj = define.cls(*args, **kwargs)
        for prop_name, prop_value in define.props.items():
            value = prop_value
            if isinstance(prop_value, BaseDef):
                value = prop_value.get_actual_value(self)
            setattr(obj, prop_name, value)
        return obj
