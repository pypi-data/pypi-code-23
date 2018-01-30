"""Multi-project build tool invoker.

A build tool to invoke a tool on a group of co-dependent projects.

Menhir `multiproject` builds a graph of the dependencies between
projects in a source repository.  It does this with the help of the
build tools.

The :doc:`setup_py` tool contributes dependencies based on
``file://..`` links in ``requirements.txt``.


Configuration
-------------

The `multiproject` key in :file:`menhir-config.yaml` is used to
configure the projects, and how :command:`menhir` discovers projects.

When ``project_graph``, ``root_projects`` and ``project_config`` are
specified in configuration, no project discovery is done.

To output discovered configuration in a form that can be saved in
:file:`menhir-config.yaml`, use the command::

    menhir multiproject --no-traverse pprint

The available keys:

``tools``
    a list of available tools to use in project discovery.
    The multiproject tool itself is always used in discovery,
    and recognises directories containing ``.menhir_project``
    or ``menhir-config.yaml`` files.

    If ``menhir-config.yaml`` contains a ``depends_on`` key, with
    a list of project relative (sub-)project paths, these are added
    to the projects dependencies.


``ignore``
    a list of directory names to ignore (all hidden directories,
    starting with a period are ignored by default, as are
    ``__pycache__`` directories).


``project_graph``
    a dict specifying dependency edges between project paths.

``root_projects``
    a list of project paths at the root of the dependency graph.

``project_config``
    a dict specify project configuration.  At present the only
    supported key is ``tools``, specify the tools the project uses.


Default configuration
---------------------

The multiproject tool propagates configuration down the source tree.
It also reads a default configuration, inherited by projects lower
down the source tree, from a :file:`menhir-defaults.yaml` file with
the same format as :file:`menhir-config.yaml`.


Git Status
----------

When run with the :command:`git_status` tool, the changed state of
each project, including dependent and dependee changes, is set, and
this information passed to the build tools that
:command:`multiproject` invokes.

Each tool provides it's own specific behaviour, depending on the the
status of each project, and on whether the changed information is
available or not.

"""
from __future__ import print_function  # NOQA

import argparse
import logging
import os.path

from menhir.fileutils import load_yaml
from menhir.tool import Tool
from menhir.tool_utils import (
    FAIL,
    NOTHING_TO_DO,
    OK,
    call_tool_chain,
    working_dir,
)
from menhir.utils import getd

log = logging.getLogger(__name__)


def tool():
    return MultiProject()


class MultiProject(Tool):

    def dir_info(tool, path, info):
        has_marker = os.path.exists(os.path.join(path, ".menhir-project"))
        has_config = os.path.exists(os.path.join(path, "menhir-config.yaml"))
        return {
            'project_recognised': has_marker or has_config,
            'can_run': True,
        }

    def dependencies(tool, path):
        config = load_yaml(os.path.join(path, 'menhir-config.yaml')) or {}
        if 'souvenir' in path:
            print('config', config)
        return config.get('depends_on', [])

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args):
        return call_tool(path, info, args)

    def build_jobs(tool, info):
        return []


def call_tool(path, info, args):
    from os.path import relpath
    from menhir.tool import load_tool

    if not args.sub_tool:
        return NOTHING_TO_DO

    root = args.root or info.get('menhir', {}).get('root')
    root = relpath(root)
    info = config_with_projects(info, root)

    config = info['multiproject']
    state = info['multiconfig']

    project_graph = config['project_graph']
    project_meta = config['project_meta']
    root_projects = config['root_projects']
    project_infos = state['project_infos']

    git_status = info.get('git_status', {})
    files = (
        git_status.get('uncommited') or
        git_status.get('changed', {}).get('all')
    )
    if files:
        update_for_changed_files(
            project_graph, project_infos, root_projects, root, files
        )

    no_traverse = args.no_traverse
    tool_name = args.sub_tool
    tool = load_tool(tool_name)
    no_traverse = no_traverse or not tool.traverse_multiproject(info)

    parser = tool.arg_parser(prog=tool_name)
    args = parser.parse_args(args.arg)

    if no_traverse:
        print('project_meta', project_meta)
        meta = project_meta.get(root, {})
        res = apply_tool_to_path(path, info, meta, tool, args)
    else:
        res = apply_tool(
            project_graph,
            project_infos,
            root_projects,
            project_meta,
            tool,
            args
        )

    if res.get('fail'):
        log.error('Build tool "%s" failed', tool_name)

    log.debug('res: %s', res)
    return res


def parser(**kwargs):
    """Arg parser for the tool options and arguments."""
    parser = argparse.ArgumentParser(
        description="Multi-project build tool invoker.",
        **kwargs
    )

    parser.add_argument(
        "--root",
        help="Specify the root of the project tree.",
    )

    parser.add_argument(
        "--no-traverse",
        default=False,
        action='store_const',
        const=True,
        help="""Only run the given command once.
The  project graph is not traversed.""",
    )

    parser.add_argument(
        "sub_tool",
        nargs="?",
        help='Tool to invoke.',
    )

    parser.add_argument(
        "arg",
        nargs=argparse.REMAINDER,
        help='Tool arguments',
    )

    return parser


def config_with_projects(info, rel_root):
    from menhir import gitutils
    rel_root = rel_root or gitutils.find_root()
    config = getd(info, 'multiproject')
    infos = getd(info, 'multiconfig')
    info['multiconfig'] = infos
    if not config.get('project_graph'):
        info = describe_repository(info, rel_root)
        config = getd(info, 'multiproject')
        infos = getd(info, 'multiconfig')

    infos['root'] = rel_root
    return info


def describe_repository(root_info, rel_root):
    """Parse the root menhir configuration."""
    from menhir.fileutils import directory_graph
    from menhir.graph import root_nodes
    from menhir.tool import default_tools, load_tool

    tools = root_info.get('menhir', {}).get('tools', default_tools())
    tool_impls = list(map(load_tool, tools))  # dict(zip(tools, ))

    config = getd(root_info, 'multiproject')

    ignore_dirs = config.get('ignore', [])
    log.debug('Ignoring: %s', ignore_dirs)

    # build the dependency graph
    fs_graph = directory_graph(rel_root, ignore_dirs)
    project_meta = config.get('project_meta')

    project_meta, infos = project_infos(
        fs_graph, rel_root, tool_impls, project_meta
    )

    graph = config.get('project_graph', project_graph(project_meta))
    roots = config.get('root_projects', root_nodes(graph, infos))

    def is_child(x, y):
        from os.path import abspath, normpath
        return normpath(abspath(y)).startswith(normpath(abspath(x)))

    roots = list(filter(lambda x: is_child('.', x), roots))

    config['project_meta'] = project_meta
    config['project_graph'] = graph
    config['root_projects'] = roots
    root_info['multiconfig'] = root_info.get('multiconfig', {})
    root_info['multiconfig']['project_infos'] = infos
    return root_info


def project_infos(graph, root, tools, project_meta):
    """Return a map of project root path to project info dict."""
    from os.path import abspath, basename
    from menhir.graph import dfs_visit
    from menhir.config import project_config

    create_meta = not bool(project_meta)
    project_meta = project_meta or {}

    infos = {}

    def calc_config(defaults, path):
        from copy import deepcopy
        from menhir.utils import deep_merge
        defaults = deep_merge(defaults, defaults_config(path))
        config = deepcopy(defaults)
        config = deep_merge(config, project_config(dir=path))
        config['multiproject'] = {}
        return defaults, config

    def pre_f(defaults, path):
        defaults, config = calc_config(defaults, path)
        if create_meta:
            used_tools = list(filter(
                lambda t: t.dir_info(path, config).get('project_recognised'),
                tools
            ))
            used = list(map(lambda x: x.name(), used_tools))
            if used:
                project_meta[path] = project_meta.get(path, {})
                project_meta[path]['tools'] = used
        else:
            used = project_meta.get(path, {}).get('tools')

        if used:
            infos[path] = config
            infos[path]['project-name'] = (
                config.get('project-name') or
                basename(abspath(path))
            )

        return defaults

    def post_f(defaults, path, child_defaults):
        return defaults

    defaults = {}
    dfs_visit(graph, root, defaults, pre_f, post_f,)

    return project_meta, infos


def defaults_config(dir_path):
    """Return the defaults configuration in dir_path."""
    from os.path import join
    return load_yaml(join(dir_path, 'menhir-defaults.yaml')) or {}


def project_graph(roots):
    """Return a project dependency graph."""
    from functools import reduce
    from menhir.tool import load_tool

    edges = {
        root: reduce(
            lambda x, y: x.union(y or set()),
            [
                set(load_tool(tool).dependencies(root))
                for tool in set(info['tools']).union({'multiproject'})
            ],
            set()
        )
        for root, info in roots.items()
        }

    return {k: list(v) for k, v in edges.items()}


def apply_tool(dependencies, infos, roots, project_meta, tool, args):
    """Apply tool to each project.

    Projects are visited in dependency order.  A full traversal is
    made.  It is up to each tool to decide whether to run, based on
    the changed state in the project info.
    """
    from functools import reduce
    from menhir.graph import dfs_visit

    log.debug('apply_tool')

    def pre_f(state, path):
        return state

    def merge_state(x, y):
        log.debug('merge_state: %s %s', x, y)
        x['failed'] = x.get('failed') or y.get('failed')
        x['seen'] = x['seen'].union(y['seen'])
        return x

    def post_f(state, path, child_states):
        log.debug('apply_tool post_f %s %s', path, state)
        info = infos[path]
        meta = project_meta[path]
        if not state.get('failed') and path not in state['seen']:
            res = apply_tool_to_path(path, info, meta, tool, args)
            if res['status'] == 'fail':
                log.warning('%s failed in %s', tool, path)
                state['failed'] = True

        seen = state['seen']
        seen.add(path)
        state['seen'] = seen
        return state

    state = {'seen': set()}
    child_states = [
        dfs_visit(
            dependencies,
            root,
            state,
            pre_f,
            post_f,
            child_state_f=lambda x: x  # shared state
        )
        for root in roots
    ]

    log.debug('child_states: %s', child_states)
    state = reduce(merge_state, child_states, state)
    log.debug('merged state: %s', state)
    if state.get('failed'):
        return FAIL
    return OK


def apply_tool_to_path(path, info, meta, tool, args):
    log.debug('Executing %s in %s', tool.name(), path)
    if not tool.dir_info(path, info).get('can_run'):
        log.debug('Tool %s not runnable in %s', tool, path)
        return NOTHING_TO_DO
    with working_dir(path):
        res = tool.execute_tool(path, info, args)
    log.debug('Execute tool %s in %s returns %s', tool.name(), path, res)
    if res['status'] != 'ok':
        log.debug('Tool %s in %s result %s', tool.name(), path, res)
        res['tool'] = tool.name()
        res['args'] = args
        res['path'] = path
        return res

    remainder = getattr(args, 'remainder', None)
    log.debug('apply_tool_to_path remainder: %s', remainder)
    if remainder:
        return call_tool_chain(path, info, remainder)
    else:
        return res


def apply_cmd_to_path(path, info, cmd):
    import subprocess
    log.info('Executing "%s" in %s', " ".join(cmd), path)

    with working_dir(path):
        rc = subprocess.call(cmd)
    log.debug('Execute cmd %s in %s returns %s', cmd, path, rc)

    if rc != 0:
        log.debug('Cmd %s in %s failed %s', cmd, path, rc)
        res = FAIL.copy()
        res.update({
            'cmd': cmd,
            'path': path
        })
        return res

    return OK


def update_for_changed_files(
        dependencies, project_infos, root_projects, prefix, files
):
    """Update project infos with changed status, given changed files.

    Updates project_infos with a `changed` map containing `self`,
    `dependees` and `dependents` fields, based on the list of changed
    files.  The `changed` key is present, even if none of it's keys
    are, so tooling knows that change information is present, and
    can modify it's behaviour accordingly.

    `prefix` allows the specification of a path prefix, to add to each
    of the project dirs, before determining if they contain any of the
    files.

    Returns a list of changed projects.

    """
    changed_projects = projects_with_files(project_infos, files, prefix)
    mark_changed(project_infos, changed_projects)
    propagate_changed(dependencies, project_infos, root_projects)
    return changed_projects


def projects_with_files(roots, files, root_prefix):
    """Filter roots that contain any of files paths.

    The roots are each prefixed with root_prefix, before comparison.
    """
    from os.path import join, normpath
    log.debug('projects_with_files:')
    log.debug(' roots: %s', roots)
    log.debug(' files: %s', files)
    roots = set(roots)
    changed_roots = set()

    for path in files:
        if len(roots):
            for root in roots.copy():
                prefix = normpath(join(root_prefix, root)) if root_prefix \
                         else root
                log.debug('prefix: %s, path: %s', prefix, path)
                if path.startswith(prefix) or (
                        prefix == '.' and not path.startswith('..')
                ):
                    log.debug('adding changed root %s', root)
                    changed_roots.add(root)
                    roots.remove(root)
        else:
            break
    return changed_roots


CHANGED = 'changed'
SELF = 'self'
DEPENDENTS = 'dependents'
DEPENDEES = 'dependees'


def mark_changed(projects, changed_projects):
    """Add a `changed` dict to each project, with `self` key boolean value."""
    for project in projects:
        projects[project][CHANGED] = {SELF: project in changed_projects}


def propagate_changed(dependencies, infos, root_projects):
    """Propagate changed info to dependees and dependents.

    `changed` nodes propagate `dependees` down the graph.
    `changed` nodes propagate `dependents` up the graph.
    """
    from menhir.graph import dfs_visit

    def pre_f(state, node):
        info = infos[node]
        if state.get(DEPENDEES):
            info[CHANGED][DEPENDEES] = True
        if info[CHANGED].get(SELF):
            state[DEPENDEES] = True
        log.debug('info pre: %s', info)
        return state

    def post_f(state, node, child_states):
        from copy import copy
        info = infos[node]
        for child_state in child_states:
            if (
                    child_state[CHANGED].get(DEPENDENTS) or
                    child_state[CHANGED].get(SELF)
            ):
                info[CHANGED][DEPENDENTS] = True
        log.debug('info post: %s', info)
        return copy(info)

    for root in root_projects:
        dfs_visit(dependencies, root, {}, pre_f, post_f)
