import io
import logging
import pathlib
import traceback
from contextlib import redirect_stdout

from .loaders import default_loader
from .bind import Bind


def _get_logger():
    return logging.getLogger(__name__)


def _print_loader_exception(e):
    msg = io.StringIO()
    with redirect_stdout(msg):
        traceback.print_exc()

    msg_lines = msg.getvalue().split('\n')
    msg_lines.append('{}: {}'.format(e.__class__.__name__, e))

    for line in msg_lines:
        _get_logger().info('LOADER: {}'.format(line))


def _action_name(name):
    return name + '_load'


class BindError(Exception):
    pass


def _get_path_property(name, explicit_bind):

    def _joined_path(self):
        path = getattr(self, _hidden_name(name))
        abs_path = self._root / str(path)

        if self._workspace is None:
            if explicit_bind:
                raise BindError(
                    "Missing workspace in PathStructure initializer. "
                    "Explicit bind for '{}' failed".format(name)
                )
            return abs_path

        action_name = _action_name(name)

        tracker = self._workspace.track(action_name)

        msg = "Action '{}' status: {}".format(
            action_name,
            tracker.status(),
        )
        _get_logger().info(msg)

        if tracker.finished():
            return abs_path

        if not tracker.started():
            _get_logger().info("Starting action: '{}'".format(action_name))
            if path.loader(abs_path, self._workspace.root, action_name):
                return abs_path
            else:
                return None
        else:
            _get_logger().info("Path not ready: '{}' in progress".format(action_name))
            return None

    return property(_joined_path)


def _hidden_name(name):
    return '_' + name


def _handle_attribute(name, value):
    if name.startswith('_'):
        return {name: value}

    if isinstance(value, Bind):
        loader = value.loader
        explicit_bind = True
    elif isinstance(value, str) or isinstance(value, pathlib.Path):
        loader = default_loader
        explicit_bind = False
    else:
        raise ValueError('PathStructure value type must be one of {}'.format(
            Bind, str, pathlib.Path,
        ))

    return {
        _hidden_name(name): Bind(str(value), loader),
        name: _get_path_property(name, explicit_bind),
    }


class PathStructureMeta(type):
    def __new__(mcs, cls_name, bases, attrib):
        mapping = {}

        for name, value in attrib.items():
            mapping.update(_handle_attribute(name, value))

        return super().__new__(mcs, cls_name, bases, mapping)
