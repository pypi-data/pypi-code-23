"""The circleci tool writes a circle.yml file to build the project.

For multiproject repos:

    menhir multiproject --no-traverse circleci

Configuration is in `menhir-config.yaml`, under the `circleci` key.
Specify `jobs` and `build` as per CircleCI's `jobs` and `workspace.build` keys
for `config.yml`.


"""
import argparse
import logging
import os


import os.path

from collections import OrderedDict

from dialogue.multi_method import method, multi

from ..fileutils import yaml_dumper
from ..tool import (
    CHECKOUT,
    CHECKOUT_STATE,
    DEPENDENCIES,
    DEPLOY,
    LINT,
    TEST,
    Tool,
    build_impl,
    default_tools,
    load_tool,
)
from ..tool_utils import (
    OK,
    tool_env,
    working_dir,
)

log = logging.getLogger(__name__)

CIRCLECI = 'circleci'


def tool():
    return Circleci()


class Circleci(Tool):

    def dir_info(tool, path, info):
        log.debug('path: %s', path)
        log.info('info: %s', info)
        root = info.get('menhir', {}).get('root', '.')
        log.debug('path: %s, root %s', path, root)
        is_root = path == root
        return {
            'project_recognised': is_root,
            'can_run': is_root,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Write a config.yml file."""
        log.info('circleci: %s %s %s', path, info, args)
        log.info('Running circleci in %s', path)
        project_name = info['project-name']
        env = tool_env()
        env['MENHIR_PROJECT'] = project_name

        log.info('Info %s', info)

        build_info = build_info_for(
            info.get('circleci', {})
        )
        config = initial_config()

        if 'multiproject' in info:
            build_multi_config(
                config,
                build_info,
                info,
            )
        else:
            tools = tools_for(path, info)
            jobs = tool_jobs(tools, info)
            build_config(
                config,
                build_info,
                info,
                tools,
                jobs,
                default_build=DEFAULT_BUILD['single'],
            )

        yaml = yaml_dumper()

        config_dir = os.path.join(path, '.circleci')
        config_file = os.path.join(config_dir, 'config.yml')
        os.makedirs(config_dir, exist_ok=True)
        with open(config_file, 'w+') as f:
            # yaml.load(f)
            yaml.dump(config, f)
        return OK

    def traverse_multiproject(tool, info):
        return False


def tools_for(path, info):
    tools = info.get('menhir', {}).get('tools', default_tools())
    tool_impls = list(map(load_tool, tools))
    used_tools = list(filter(
        lambda t: t.dir_info(path, info).get('project_recognised'),
        tool_impls
    ))
    return used_tools


def tool_jobs(tools, info):
    jobs = []
    for tool in tools:
        jobs.extend(tool.build_jobs(info))
    return jobs


def build_info_for(info):
    log.debug('build_info_for  %s', info)
    build_info = {
        'default': docker(DEFAULT_DOCKER),
        'use_pyenv': False,
        'workspace': '/workspace',
    }
    build_info.update(info.get('build', {}))
    return build_info


def initial_config():
    config = OrderedDict(**PREAMBLE)
    config['jobs'] = {}
    config['workflows'] = {
        'version': 2,
        'build': {'jobs': []},
    }
    return config


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Write circleci config",
        **kwargs
    )
    parser.add_argument('args', nargs='*', help='circleci arguments')
    return parser


PREAMBLE = {
    'version': 2,
}

DEFAULT_DOCKER = {
    'image': 'hadrien/pythonci',
    'user': 'root',
}


def requires(jobs):
    return {
        'requires': jobs,
    }


DEFAULT_BUILD = {
    'single': {
        'jobs': [
            {CHECKOUT: {}},
            {DEPENDENCIES: requires([CHECKOUT])},
            {TEST: requires([DEPENDENCIES])},
            {LINT: requires([DEPENDENCIES])},
            {DEPLOY: requires([TEST, LINT])},
            # {'integration_test': requires(['deploy'])},
        ]
    },
    'multi': {
        'jobs': [
            {CHECKOUT: {}},
            {DEPENDENCIES: requires([CHECKOUT])},
            {TEST: requires([DEPENDENCIES])},
            {LINT: requires([DEPENDENCIES])},
            {DEPLOY: requires([TEST, LINT])},
            # {'integration_test': requires(['deploy'])},
        ]
    }
}

ROOT_TASKS = {CHECKOUT, CHECKOUT_STATE}


def build_multi_config(config, build_info, info):
    projects = info['multiproject']['project_meta']
    for path, meta in projects.items():
        deps = info['multiproject']['project_graph'][path]
        project_info = info['multiconfig']['project_infos'][path]
        tool_names = meta['tools']
        tools = list(map(load_tool, tool_names))
        jobs = tool_jobs(tools, info)
        build_config(
            config,
            build_info,
            project_info,
            tools,
            jobs,
            path=path,
            suffix=project_suffix(project_info['project-name']),
            deps=[
                project_suffix(dep)
                for dep in deps
            ],
            default_build=DEFAULT_BUILD['multi'],
        )


def project_suffix(project_name):
    return '_' + project_name


def build_config(
        config,
        build_info,
        info,
        tools,
        tool_jobs,
        path='.',
        suffix="",
        deps=[],
        default_build=DEFAULT_BUILD,
):
    """Update config with build tasks for project at path.

    path   - path to project, relative to project root
    suffix - project specific suffix for task names
    deps   - list of project paths of dependencies
    """
    log.debug('xx build_info %s', build_info)
    build_spec = build_info.get('build', default_build)
    build_jobs = []
    jobs = OrderedDict()

    for job in build_spec['jobs']:
        requires = []
        job_type, job_spec = list(job.items())[0]

        if job_type not in tool_jobs:
            continue

        if job_type in ROOT_TASKS:
            requires = job_spec.get('requires', [])
            job_name = job_type
        else:
            job_name = job_type + suffix
            for require in job_spec.get('requires', []):
                if require in ROOT_TASKS:
                    requires.append(require)
                else:
                    requires.append(require + suffix)
                    for dep in deps:
                        requires.append(require + dep)
        log.info('Write job: %s %s', job_name, job_spec)

        spec = {'requires': requires}
        build_flows, job_specs = spec_for(
            build_info, job_type, path, job_name, spec, info, tools,
        )
        log.info('flow, job: %s %s', build_flows, job_specs)
        build_jobs.extend(build_flows)
        jobs.update(job_specs)

    config['jobs'].update(jobs)
    config['workflows']['build']['jobs'].extend(build_jobs)

    return config


@multi
def spec_for(build_info, job_type, path, job_name, job_spec, info, tools):
    return job_type


def build_spec_for(
        build_info, job_type, path, job_name, job_spec, info, tools,
        load_cache_keys,
        save_cache_keys={},
        extra_steps=[],
):
    job_detail = OrderedDict(**build_info['default'])
    job_detail.update({
        'steps': [restore_cache(key) for key in load_cache_keys],
    })

    log.debug('xxinfo %s', info)
    steps = info_steps(info, job_type)
    log.debug('steps %s', steps)

    if steps:
        job_detail['steps'].extend(steps)
    else:
        invocations = [
            x
            for tool in tools
            for x in build_impl(tool, job_type, CIRCLECI, info)
        ]
        job_detail['steps'].extend(filter(lambda x: x, invocations))
        job_detail['steps'].extend(extra_steps)

    job_detail['steps'].extend(
        [
            save_cache(cache_key, paths)
            for cache_key, paths in save_cache_keys.items()
        ]
    )
    job_detail.update(working_directory(build_info, path))
    return [{job_name: job_spec}], {job_name: job_detail}


@method(spec_for)
def spec_for_default(
        build_info, job_type, path, job_name, job_spec, info, tools
):
    return build_spec_for(
        build_info, job_type, path, job_name, job_spec, info, tools,
        [source_cache_key(info), dependencies_cache_key(info)])


@method(spec_for, CHECKOUT)
def spec_for_checkout(
        build_info, job_type, path, job_name, job_spec, info, tools
):
    return build_spec_for(
        build_info, job_type, path, job_name, job_spec, info, tools,
        [], {source_cache_key(info): [build_info['workspace']]})


@method(spec_for, DEPENDENCIES)
def spec_for_dependencies(
        build_info, job_type, path, job_name, job_spec, info, tools
):
    if is_subproject(info):
        cache_paths = [
            "/home/circleci/.pyenv/versions/3.6.1/envs/"
            "{}/lib/python3.6/site-packages"
            .format(info["project-name"])
        ]
    else:
        cache_paths = [
            '/root/.cache/',
            '/usr/local/lib/python3.6/site-packages',
            '/usr/local/bin'
        ]
    return build_spec_for(
        build_info, job_type, path, job_name, job_spec, info, tools,
        [source_cache_key(info)],
        {dependencies_cache_key(info): cache_paths})


@method(spec_for, CHECKOUT_STATE)
def spec_for_checkout_state(
        build_info, job_type, path, job_name, job_spec, info, tools
):
    return build_spec_for(
        build_info, CHECKOUT, path, job_name, job_spec, info, tools,
        [], {source_cache_key(info): [build_info['workspace']]},
        extra_steps=[
            'menhir git_status multiproject write_state',
        ]
    )


def info_steps(info, job):
    return info.get('circleci', {}).get('jobs', {}).get(job, {}).get('steps')


def working_directory(build_info, path):
    return {
        'working_directory': os.path.join(build_info['workspace'], path),
    }


def docker(spec):
    return {
        'docker': [spec],
    }


def source_cache_key(info):
    return "repo-{{ .Environment.CIRCLE_SHA1 }}"


def dependencies_cache_key(info):
    name = info['project-name']
    return (
        'pydep-%s'
        # TODO - remove the SHA from the key
        '-{{ .Environment.CIRCLE_SHA1 }}'
        '-{{ checksum "requirements.txt" }}'
        '-{{ checksum "requirements-tests.txt" }}'
    ) % name


def restore_cache(cache_key):
    return {
        'restore_cache': {
            'key': cache_key,
        }
    }


def save_cache(cache_key, paths):
    return {
        'save_cache': {
            'key': cache_key,
            'paths': paths,
        }
    }


def run(name, invocations):
    return {
        'run': {
            'name': name,
            'command': "\n".join(invocations)
        },
    }


def is_subproject(info):
    return 'multiproject' in info


@method(build_impl, ('git', CHECKOUT, CIRCLECI))
def build_impl_git_checkout_circleci(tool, task, build_env, info):
    if is_subproject(info):
        return [
            {'checkout': {}},
            run('Write state', [
                'pip install menhir==$(cat .menhir-version)',
                'menhir git_status multiproject write_state',
            ]),

        ]
    else:
        return [{'checkout': {}}]


@method(build_impl, ('pyenv', DEPENDENCIES, CIRCLECI))
def build_impl_pyenv_dependencies_circleci(tool, task, build_env, info):
    is_multi = 'multiproject' in info
    if is_multi:
        return [run('Install Dependencies', ["menhir pyenv virtualenv"])]
    else:
        return [run(
            'Install Test Dependencies',
            ["[test -f requirements-tests.txt] && "
             "pip install -r requirements-tests.txt"])]


@method(build_impl, ('setup_py', DEPENDENCIES, CIRCLECI))
def build_impl_setup_py_dependencies_circleci(tool, task, build_env, info):
    is_multi = 'multiproject' in info
    if not is_multi:
        return [run('Install Dependencies', ["pip install ."])]
    else:
        return []


@method(build_impl, ('setup_py', TEST, CIRCLECI))
def build_impl_setup_py_test_circleci(tool, task, build_env, info):
    return [run('Test', ["menhir -v setup_py test"])]


@method(build_impl, ('codecov', TEST, CIRCLECI))
def build_impl_codecov_test_circleci(tool, task, build_env, info):
    return [run('Test', ["menhir -v codecov"])]


# @method(build_impl, ('pylama', LINT, CIRCLECI))
# def build_impl_pylama_lint_circleci(tool, task, build_env, info):
#     return [run('Test', ["menhir -v pylama"])]


@method(build_impl, ('docker', DEPLOY, CIRCLECI))
def build_impl_docker_push_circleci(tool, task, build_env, info):
    return [run('Deploy docker', [
        "$(aws --region ca-central-1 ecr get-login --no-include-email)",
        "menhir docker publish",
    ])]
