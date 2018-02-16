import logging

import os

from .loaders import default_loader
from .bind import Bind


def _get_logger():
    return logging.getLogger(__name__)


def _get_path_property(name):

    def _joined_path(self):
        bind_obj = self._path_meta[name].path  # type: Bind
        abs_path = os.path.join(self._root, bind_obj)

        action = bind_obj.action()

        tracker = self.track(action)

        msg = "Action '{}' status: {}".format(
            action,
            tracker.status(),
        )
        _get_logger().info(msg)

        if tracker.finished():
            return Bind(abs_path)

        if not tracker.started():
            _get_logger().info("Starting action: '{}'".format(action))
            bind_obj.loader(
                str(abs_path),
                str(self._root),
                str(action),
            )

            msg = "Action '{}' status: {}".format(action, tracker.status())
            _get_logger().info(msg)

            if tracker.finished():
                return Bind(abs_path)
        else:
            _get_logger().info("Path not ready: '{}' in progress".format(action))

        return None

    return property(_joined_path)


class CustomProperty(property):
    def __init__(self, p, action):
        super().__init__(p.fget, p.fset, p.fdel)
        self.action = action


def _get_loader(value):

    if isinstance(value, Bind):
        loader = value.loader
    elif isinstance(value, str):
        loader = default_loader
    else:
        raise ValueError('PathStructure value type must be one of {}, found: {}'.format(
            (Bind, str), type(value)
        ))

    return loader


def _handle_attribute(name, value):
    if name.startswith('_') or name == 'track':
        return {}

    loader = _get_loader(value)

    meta = _PathItemMeta(
        Bind(str(value), loader),
        _get_path_property(name),
    )
    meta.prop = CustomProperty(meta.prop, meta.path.action)
    return meta


class _PathItemMeta:
    def __init__(self, path, prop):
        self.path = path
        self.prop = prop


class PathStructureMeta(type):
    def __new__(mcs, cls_name, bases, attrib):
        paths = {}

        for base in bases:
            _paths = getattr(base, '_path_meta')
            paths.update(_paths)

        for name, value in attrib.items():
            meta = _handle_attribute(name, value)
            if meta:
                paths.update({name: meta})

        attrib['_path_meta'] = paths

        for path, meta in paths.items():
            attrib[path] = meta.prop

        return super().__new__(mcs, cls_name, bases, attrib)


