"""The ecs-deploy tool provides a task to deploy a docker image to ECS.

It uses the `ecs-deploy` script from:
    https://github.com/silinternational/ecs-deploy


The `install` task will install the ecs-deploy tool from github.

The `deploy` task will deploy the current project's docker image to ECS.
Relies on `ecs-deploy` and the AWS CLI being on `PATH`.

"""
import argparse
import logging
from functools import reduce

from menhir.project import image
from menhir.tool import Tool
from menhir.tool_config import value_array
from menhir.tool_utils import (
    FAIL,
    NOTHING_TO_DO,
    OK,
    argv_to_dict,
    call,
    changed_state,
    has_self_or_dependent_changes,
    tool_env,
)
from menhir.utils import method, multi


# Guard against installation from multiple projects
installed = False


log = logging.getLogger(__name__)


def tool():
    return EcsDeploy()


class EcsDeploy(Tool):

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


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Tool for ecs-deloy."
    )
    parsers = parser.add_subparsers(
        help="EcsDeploy commands",
        dest='phase'
    )

    p = parsers.add_parser(
        'install',
        help="Download and install ecs-deploy"
    )

    p.add_argument(
        '--version',
        default='master',
        help='version (git tag or branch)',
    )
    p.add_argument(
        '--target',
        default='/usr/local/bin',
        help='target directory')
    p.add_argument(
        '--source',
        default='https://github.com/silinternational/'
        'ecs-deploy/raw/{}/ecs-deploy',
        help='Distribution source')
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'deploy',
        help="Deploy docker image with ecs-deploy"
    )

    p.add_argument(
        '--arg', dest='args', action='append',
        help="Specify an argument for the encryption settings")
    p.add_argument(
        '--region',
        help='AWS region to deploy into',
    )
    p.add_argument(
        '--cluster',
        help='AWS cluster to deploy into',
    )
    p.add_argument(
        '--service-name',
        help='ECS service name to deploy into',
    )
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    return parser


@multi
def task(path, info, config, args):
    """Execute a task."""
    return args.phase


@method(task, 'install')
def task_install(path, info, config, args):
    import stat

    from os import chmod
    from os.path import join
    from tqdm import tqdm
    import requests

    global installed

    if installed:
        return NOTHING_TO_DO

    version = args.version
    target = args.target

    url = args.source.format(version)
    target_file = join(target, 'ecs-deploy')

    print(url)
    with open(target_file, 'wb+') as f:
        response = requests.get(url, stream=True)
        for data in tqdm(response.iter_content(chunk_size=1024)):
            f.write(data)

    chmod(target_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    installed = True
    return OK


@method(task, 'deploy')
def task_deploy(path, info, config, args):
    log.info('Deploying docker container to ECS in %s', path)

    changed = changed_state(info)
    if not has_self_or_dependent_changes(changed):
        return NOTHING_TO_DO

    project_name = info['project-name']

    env = tool_env()
    env['MENHIR_TAG'] = project_name

    deploy_info = info.get('ecs_deploy', {})

    arg_names = deploy_info.get('args', [])
    arg_values = args.args or []

    arg_dict = argv_to_dict(arg_names, arg_values)

    sha_tag = image(info, path)
    sha_tag = sha_tag % arg_dict
    if not sha_tag:
        log.error('No docker image configured to deploy.')
        return FAIL

    arg_args = {k: v for k, v in vars(args).items() if v is not None}

    value_names = ['sha', 'image']
    values = value_array(
        value_names,
        info, path,
        arg_dict
    )
    values_dict = {k: v for k, v in zip(value_names, values)}

    vargs = deploy_info.copy()
    vargs.update(arg_dict)
    vargs.update(values_dict)
    vargs.update(arg_args)

    deploy_args = [
        ['--{}'.format(arg.replace('_', '-')), str(vargs.get(arg)) % vargs]
        for arg in ['cluster', 'region', 'service_name', 'timeout']
        if arg in vargs and vargs[arg] is not None
    ]
    deploy_args = reduce(lambda x, y: x + y, deploy_args, [])
    image_args = ['--image', sha_tag]
    tag = str(vargs.get("tag", "")) % vargs
    if tag:
        image_args = ['--image', 'ignore', '--tag-only', tag]
    argv = ['ecs-deploy'] + deploy_args + image_args
    log.debug('deploy with: %s', argv)
    return call(argv, env=env,)
