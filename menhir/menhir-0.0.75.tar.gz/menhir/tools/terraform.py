"""Terraform tool.

Provides ``plan``, ``apply`` and ``destroy`` tasks for terrform, managing
remote-state.

Configuration is under the ``terraform`` key.

The ``targets`` key contains a dict for each target directory under
``source-dir`` (defaults to ``infra``).  Each infra directory is
configured as a dict under the directory's name.

Arguments
---------

A directory can be configures with ``args``, a list containing the names
of values it expects to be passed on the command line.


Vars passed to Terraform
------------------------

The ``values`` key configures a list of names for values to be passed
to terraform.

``values`` can contain names from ``args`` and the following:

project        the name of the project
branch         the current branch name
branch-slug    the current branch name, sanitised
sha            the current commit sha as a hex string
sha-mod-1024   the current as a decimal modulo 1024

The ``values`` list can also contain items of the form ``name=value``,
which will pass the var ``name`` to terraform, with the value
calculated according to ``value`` from the list above.

Remote Config
-------------

The remote state is configured independently of the target direcotry
using the `remote-config` key.  The value contains a `backend` string
specifying the terraform backend, and a `backend-config` dict
specifying the backend specific configuration.

The `remote-config` key is also supported at the target directory
level.  For consistency, usage at this level is not recommended.

The only supported backend at present is ``s3``.  It expects
``bucket``, ``key`` and ``region`` values.  The ``key`` configuration
value is a format string, with can use any of the ``values`` and
``args`` configuration values.  It can also use ``target`` to refer to
the target name.

"""
import argparse
import logging
import subprocess
from functools import reduce

from menhir.tool import Tool
from menhir.tool_utils import FAIL, NOTHING_TO_DO, OK, tool_env, working_dir
from menhir.utils import method, multi

log = logging.getLogger(__name__)


def tool():
    return Terraform()


class Terraform(Tool):

    def dir_info(tool, path, info):
        from os.path import isdir, join
        path = join(
            path,
            info.get('terraform', {}).get('source-dir', 'infra')
        )
        has_terraform = isdir(path)
        return {
            'project_recognised': has_terraform,
            'can_run': has_terraform,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args):
        """Execute a build phase."""
        config = info.get('terraform', {})
        return task(path, info, config, args)

    def build_jobs(tool, info):
        return []


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Tool for terraform."
    )
    parsers = parser.add_subparsers(
        help="Terraform commands",
        dest='phase'
    )

    p = parsers.add_parser(
        'apply',
        help='Apply a terraform infrastructure directory'
    )
    p.add_argument('directory', nargs=1)
    p.add_argument('args', nargs="*")

    p = parsers.add_parser(
        'plan',
        help='Plan a terraform infrastructure directory'
    )
    p.add_argument('directory', nargs=1)
    p.add_argument('args', nargs="*")

    p = parsers.add_parser(
        'destroy',
        help='Destroy a terraform infrastructure directory'
    )
    p.add_argument('directory', nargs=1)
    p.add_argument('args', nargs="*")

    p = parsers.add_parser(
        'install',
        help="Download and install terraform"
    )

    os, arch = platform()
    p.add_argument('ver', nargs=1, help='version')
    p.add_argument(
        '--os',
        default=os,
        help='Operating system',
        choices=['darwin', 'linux', 'freebsd', 'openbsd', 'solaris'],
    )
    p.add_argument(
        '--arch',
        default=arch,
        help='Architecture',
        choices=['amd64', '386', 'arm'],
    )
    p.add_argument(
        '--target',
        default='/usr/local/bin',
        help='target directory')
    p.add_argument(
        '--source',
        default='https://releases.hashicorp.com/terraform',
        help='Distribution source')
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    return parser


@multi
def task(path, info, config, args):
    """Execute a task."""
    return args.phase


@method(task)
def task_action(path, info, config, args):
    return action(args.phase, path, info, config, args)


def action(action, path, info, config, args):
    """Invoke a terraform action on the given path."""
    from os import getenv
    from os.path import exists, join
    from menhir.tool_config import aliased_value_array
    from menhir.tool_utils import call
    from menhir.utils import deep_merge

    log.debug('terraform config: %(config)s', dict(config=config))
    infra_dir = join(path, config.get('source-dir', 'infra'))

    if not exists(infra_dir):
        log.debug('No infra directory in %(path)s', {'path': path})
        return NOTHING_TO_DO

    directory = args.directory[0]
    run_flag = (
        'changed' not in info or
        info['changed'].get('self') or
        info['changed'].get('dependents')
    )
    project_dir = join(infra_dir, args.directory[0])
    project_dir_exists = exists(project_dir)

    run = project_dir_exists and (run_flag or action == 'destroy')
    log_run(run, args.phase, directory, path)

    if not run:
        return NOTHING_TO_DO

    dconfig = config.get('targets', {}).get(directory, {})
    dargs = dconfig.get('args', [])
    dvalues = dconfig.get('values', [])
    remote_config = config.get('remote-config')
    dremote_config = dconfig.get('remote-config', {})
    remote_config = deep_merge(remote_config or {}, dremote_config)

    if len(args.args or []) < len(dargs):
        log.error(
            'Not enough arguments to terraform apply %(directory)s: '
            'expected: %(expected)s, got: %(got)s',
            {
                'directory': directory,
                'expected': dargs,
                'got': args.args,
            }
        )
        return FAIL

    arg_dict = dict(zip(dargs, args.args))

    def format_value(x):
        return '%s="%s"' % x

    values_list = aliased_value_array(dvalues, info, path, arg_dict)
    values = list(map(format_value, values_list))

    values_dict = {k: v for k, v in values_list}
    values_and_args = {
        'target': directory,
        'project': info['project-name'],
    }
    values_and_args.update(arg_dict)
    values_and_args.update(values_dict)

    values_and_args = {
        k: v % values_and_args if isinstance(v, str) else v
        for k, v in values_and_args.items()
    }

    def extend_var(x, y):
        x.extend(['-var', y])
        return x

    var_args = reduce(extend_var, values, [],)

    project_name = info['project-name']

    env = tool_env()

    tf_log = getenv('TF_LOG')
    if tf_log:
        env['TF_LOG'] = tf_log

    with working_dir(project_dir):
        if remote_state(remote_config, project_name, values_and_args):
            return FAIL
        log.info("terraform get %s", env)
        res = call(["terraform", "get"], env=env,)
        if res != OK:
            return res
        log.info("terraform %s %s", action, var_args)
        return call(["terraform", action] + var_args, env=env,)


def log_run(cond, task, directory, path):
    txt = None
    if cond:
        txt = 'Run %(task)s in %(path)s'
    else:
        txt = 'Not run %(task)s in %(path)s'

    log.info(txt, {'task': task, 'directory': directory, 'path': path})


def remote_state(remote_config, project, values):
    import shutil

    tf_version = terraform_version()
    log.debug('terraform version: %s', tf_version)

    use_remote_config = tf_version < "0.9.0"
    backend = remote_config.get('backend')
    backend_config = remote_config.get('backend-config')

    if not backend:
        log.warning('remote-state configured, but no backend specified')
        return None

    if not backend_config:
        log.warning(
            'remote-state configured, but no backend_config specified'
        )
        return None

    shutil.rmtree('.terraform', ignore_errors=True)
    return remote_state_backend(
        backend, backend_config, project, values, use_remote_config
    )


def terraform_version():
    proc = subprocess.Popen(["terraform", "--version"], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    if lines:
        words = lines[0].split()
        version = words[1]
        return version[1:].decode('utf-8')  # drop the leading 'v'


@multi
def remote_state_backend(
        backend, backend_config, project, values, use_remote_config
):
    """Configure a remote backend."""
    return backend


@method(remote_state_backend, 's3')
def remote_state_s3(
        backend, backend_config, project, values, use_remote_config
):
    from os import getenv
    from os.path import join
    from subprocess import call

    bucket = backend_config.get('bucket')
    if not bucket:
        log.warning('terraform remote-state s3: no bucket specified')
        return None

    env = tool_env()

    tf_log = getenv('TF_LOG')
    if tf_log:
        env['TF_LOG'] = tf_log

    if use_remote_config:
        key = backend_config['key']
        key = key % values
        key = join(key, "terraform.tfstate")
        region = backend_config.get('region', "us-east-1")

        log.info(
            'State from s3://%(bucket)s/%(key)s in %(region)s',
            {
                'bucket': bucket,
                'key': key,
                'region': region,
            }
        )

        cmd = [
                "terraform", "remote", "config",
                "-backend=s3",
                "-backend-config=bucket=%s" % bucket,
                "-backend-config=key=%s" % key,
                "-backend-config=region=%s" % region,
            ]
        log.debug('%s %s', cmd, env)

        return call(cmd, env=env)
    else:

        def extend_var(x, y):
            x.extend(['-backend-config=%s=%s' % y % values])
            return x

        bc = reduce(extend_var, backend_config.items(), [],)

        cmd = [
            "terraform", "init",
        ] + bc

        log.debug('%s %s', cmd, env)
        return call(cmd, env=env)


# Guard against installation from multiple projects
installed = False


@method(task, 'install')
def task_install(path, info, config, args):
    import shutil
    import stat
    import zipfile

    from os import chmod
    from os.path import join
    from tempfile import TemporaryFile
    from tqdm import tqdm
    import requests

    global installed

    if installed:
        return NOTHING_TO_DO

    version = args.ver[0]
    os = args.os
    arch = args.arch
    target = args.target

    file_name = 'terraform_%s_%s_%s.zip' % (version, os, arch)
    url = "%s/%s/%s" % (
        args.source,
        version,
        file_name
    )
    target_file = join(target, 'terraform')

    print(url)
    with TemporaryFile() as f:
        response = requests.get(url, stream=True)
        for data in tqdm(response.iter_content(chunk_size=1024*1024)):
            f.write(data)

        with zipfile.ZipFile(f) as z:
            with z.open("terraform") as zf, open(target_file, 'wb') as f:
                shutil.copyfileobj(zf, f)

    chmod(target_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    installed = True
    return OK


def platform():
    import platform
    arch = {
        'x86_64': 'amd64',
    }

    system = platform.system().lower()
    machine = platform.machine()

    return system, arch.get(machine, machine)
