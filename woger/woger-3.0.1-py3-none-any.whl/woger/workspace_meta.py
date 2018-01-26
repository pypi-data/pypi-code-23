import logging
import pathlib

import os

from .path import Path


def _get_logger():
    return logging.getLogger(__name__)


def _get_path_property(hidden_name):

    loader_triggered = False

    def _joined_path(self):
        nonlocal loader_triggered

        path = getattr(self, hidden_name)
        abs_path = self._root / str(path)

        if not loader_triggered:
            _get_logger().info('Running loader for {}'.format(path))
            try:
                path.loader(abs_path, workspace=self._workspace)
            except Exception as e:
                _get_logger().warning('Loader for {} failed: {}'.format(path, e))
                return None

            _get_logger().info('Finished: loader for {}'.format(path))
            loader_triggered = True

        return abs_path

    return property(_joined_path)


def default_loader(path: pathlib.Path, **kwargs):
    is_dir = '.' not in path.name

    if is_dir:
        os.makedirs(str(path))


class PathStructureMeta(type):
    def __new__(mcs, cls_name, bases, attrib):
        mapping = {}

        for name, value in attrib.items():
            if name.startswith('_'):
                mapping[name] = value
                continue

            hidden_name = '_' + name

            if isinstance(value, Path):
                loader = value.loader
            elif isinstance(value, str) or isinstance(value, pathlib.Path):
                loader = default_loader
            else:
                raise ValueError('PathStructure value type must be one of {}'.format(
                    Path, str, pathlib.Path,
                ))

            mapping[hidden_name] = Path(str(value), loader)
            mapping[name] = _get_path_property(hidden_name)

        return super().__new__(mcs, cls_name, bases, mapping)
