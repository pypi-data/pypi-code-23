"""Tool interface for tool implementations.

A tool is implemented as an opaque class.

"""
import logging

from dialogue.multi_method import method, multi

log = logging.getLogger(__name__)


CHECKOUT = 'checkout'
CHECKOUT_STATE = 'checkout_state'
DEPENDENCIES = 'dependencies'
TEST = 'test'
LINT = 'lint'
PACKAGE = 'package'
DEPLOY = 'deploy'


def missing_impl(tool, f):
    raise Exception(
        'incorrect tool implementation',
        'Tool implementation %s is missing a "%s" implementation' % (
            type(tool),
            f,
        )
    )


class Tool(object):
    """The Tool interface implemented by each tool."""
    def __str__(self):
        return "<%s>" % type(self).__name__

    def __repr__(self):
        return "<%s>" % type(self).__name__

    def name(self):
        """Return the name of the tool on the command line."""
        return type(self).__name__.lower()

    def dir_info(tool, path, info):
        """Return info about using the tool in the specified path."""
        missing_impl(tool, Tool.dir_info.__name__)

    def dependencies(tool, path):
        """Return a list of dependency prefixes for the project at path."""
        missing_impl(tool, Tool.dependencies.__name__)

    def configure_parser(tool, parser):
        """Configure arg parser for the tool options and arguments."""
        missing_impl(tool, Tool.add_arg_parser.__name__)

    def execute_tool(tool, path, info, args):
        """Execute a build phase."""
        missing_impl(tool, Tool.execute_tool.__name__)

    def build_jobs(tool, info):
        """Return build job specs."""
        missing_impl(tool, Tool.build_jobs.__name__)

    def traverse_multiproject(tool, info):
        """Predicate for multiproject traversal.

        Allow tools that do not expect traversal (eg. to do something only in
        the project root).

        """
        return True


def load_tool(tool_name):
    """Load the tool implementation for the given tool name."""
    builtin = 'menhir.tools.%s' % tool_name
    tool, e1 = require_tool(builtin)
    if not tool:
        tool, e2 = require_tool(tool_name)
    if not tool:
        raise Exception(
            'configuration_error',
            'Tool not found: "%s".  import %s gave %s.  import %s gave %s' % (
                tool_name,
                builtin, e1,
                tool_name, e2
            ))
    return tool


def require_tool(tool_path):
    from importlib import import_module
    try:
        m = import_module(tool_path)
        return m.tool(), None
    except Exception as e:
        log.debug('Failed to import: %s, "%s"', tool_path, e)
        return None, e


def default_tools():
    """Return a list of the default tool names."""
    from menhir.tools import all_tools
    return all_tools


@multi
def build_impl(tool, task, build_env, info):
    """Multi-method to return invocations for tool to run task on buildenv."""
    return tool.name(), task, build_env


@method(build_impl)
def build_impl_default(tool, task, build_env, info):
    return []
