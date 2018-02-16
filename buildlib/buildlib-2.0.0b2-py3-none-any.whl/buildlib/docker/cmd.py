from typing import Optional, List, Union
import re
from processy import run
from functools import reduce
from cmdi import command, CmdResult, CustomCmdResult


def _image_exists(
    image: str
) -> bool:
    """"""
    result = run(
        cmd=['docker', 'inspect', '--type=image', image],
        verbose=False,
        return_stdout=True
    )

    return 'Error: No such image' not in result.stdout


def _parse_option(
    args: Union[bool, list, str],
    flag: str,
) -> list:
    """"""
    if type(args) == list:
        nested = [[flag, f] for f in args]
        return reduce(lambda x, y: x + y, nested)
    elif type(args) == str:
        return [flag, args]
    elif type(args) == bool:
        return [flag] if args is True else []
    else:
        return []


@command
def run_container(
    image: str,
    add_host: Optional[List[str]] = None,
    env: Optional[List[str]] = None,
    network: Optional[str] = None,
    publish: Optional[List[str]] = None,
    volume: Optional[List[str]] = None,
    **cmdargs,
) -> CmdResult:
    """
    Run Docker container locally.
    """

    options = [
        *_parse_option(add_host, '--add-host'),
        *_parse_option(env, '-e'),
        *_parse_option(network, '--network'),
        *_parse_option(publish, '-p'),
        *_parse_option(volume, '-v'),
    ]

    p = run(['docker', 'run', '-d'] + options + [image])


@command
def stop_container(
    by_port: Union[int, str],
    **cmdargs,
) -> CmdResult:
    if by_port:
        cmd = ['docker', 'ps', '-q', '--filter', f'expose={by_port}',
               '--format="{{.ID}}"']

    ids = run(
        cmd=cmd,
        return_stdout=True,
    ).stdout.split('\n')

    ps = [
        run(['docker', 'stop', id_.replace('"', '')])
        for id_
        in ids
        if id_
    ]


@command
def kill_container(
    by_port: Union[int, str],
    **cmdargs,
) -> CmdResult:
    """"""
    if by_port:
        cmd = ['docker', 'ps', '-q', '--filter', f'expose={by_port}',
               '--format="{{.ID}}"']

    ids = run(
        cmd=cmd,
        return_stdout=True,
    ).stdout.split('\n')

    ps = [
        run(['docker', 'kill', id_.replace('"', '')])
        for id_
        in ids
        if id_
    ]


@command
def remove_image(
    image: str,
    force: bool = True,
    **cmdargs,
) -> CmdResult:
    """"""
    if _image_exists(image):
        options = [
            *_parse_option(force, '--force'),
        ]

        cmd = ['docker', 'rmi', image] + options
        p = run(cmd)


@command
def rm_dangling_images(
    force: bool = True,
    **cmdargs,
) -> CmdResult:
    """"""

    ids = run(
        cmd=['docker', 'images', '-f', 'dangling=true', '-q'],
        return_stdout=True,
    ).stdout.split('\n')

    ps = [
        remove_image(id_, force=force)
        for id_
        in ids
        if id_
    ]


@command
def tag_image(
    src_image: str,
    registry: Optional[str] = None,
    namespace: Optional[str] = None,
    dst_image: Optional[str] = None,
    tag_latest: Optional[bool] = False,
    **cmdargs,
) -> CmdResult:
    """
    """

    registry = registry + '/' if registry else ''
    namespace = namespace + '/' if namespace else ''
    dst_image = dst_image or src_image

    cmds = [['docker', 'tag', src_image, f'{registry}{namespace}{dst_image}']]

    if tag_latest:
        base_name = re.search('.*[:]', dst_image) or dst_image
        latest = f'{base_name}:latest'

        tag_cmd = ['docker', 'tag', dst_image, f'{registry}{namespace}{latest}']

        cmds.insert(1, tag_cmd)

    ps = [run(cmd, verbose=True) for cmd in cmds]


@command
def push_image(
    image: str,
    registry: Optional[str],
    namespace: Optional[str],
    **cmdargs,
) -> CmdResult:
    """
    """

    registry = registry + '/' if registry else ''
    namespace = namespace + '/' if namespace else ''

    cmd = ['docker', 'push', f'{registry}{namespace}{image}']

    p = run(cmd, verbose=True)


@command
def build_image(
    tag: List[str],
    build_arg: List[str] = None,
    dockerfile: str = 'Dockerfile',
    **cmdargs,
) -> CmdResult:
    """
    """

    options = [
        *_parse_option(build_arg, '--build-arg'),
        *_parse_option(tag, '-t'),
    ]

    cmd = ['docker', 'build', '.', '--pull', '-f', dockerfile] + options

    p = run(cmd)
