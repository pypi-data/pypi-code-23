from typing import Optional, List, Union
import re
from processy import run
from cmdinter import CmdFuncResult, Status
from functools import reduce


def _image_exists(image) -> bool:
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


def run_container(
    image: str,
    add_host: Optional[List[str]] = None,
    env: Optional[List[str]] = None,
    network: Optional[str] = None,
    publish: Optional[List[str]] = None,
    volume: Optional[List[str]] = None,
) -> CmdFuncResult:
    """
    Run Docker container locally.
    """
    title = 'Run Docker Container.'

    options = [
        *_parse_option(add_host, '--add-host'),
        *_parse_option(env, '-e'),
        *_parse_option(network, '--network'),
        *_parse_option(publish, '-p'),
        *_parse_option(volume, '-v'),
    ]

    p = run(['docker', 'run', '-d'] + options + [image])

    if p.returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )


def stop_container(
    by_port: Union[int, str],
) -> CmdFuncResult:
    title = 'Stop Docker Container'

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

    returncode = max([p.returncode for p in ps]) if ps else 0

    if returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )


def kill_container(
    by_port: Union[int, str],
) -> CmdFuncResult:
    title = 'Stop Docker Container'

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

    returncode = max([p.returncode for p in ps]) if ps else 0

    if returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )


def remove_image(
    image: str,
    force: bool = True,
) -> CmdFuncResult:
    """"""
    title = 'Remove Docker Image.'

    options = [
        *_parse_option(force, '--force'),
    ]

    cmd = ['docker', 'rmi', image] + options

    if _image_exists(image):
        p = run(cmd)
        returncode = p.returncode
    else:
        returncode = 0

    if returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )


def rm_dangling_images(
    force: bool = True
) -> CmdFuncResult:
    """"""
    title = 'Remove Dangling Docker Images.'

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

    returncode = max([p.returncode for p in ps]) if ps else 0

    if returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )


def tag_image(
    src_image: str,
    registry: Optional[str] = None,
    namespace: Optional[str] = None,
    dst_image: Optional[str] = None,
    tag_latest: Optional[bool] = False,
):
    """
    """
    title = 'Tag Docker Image.'

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

    returncode = max([p.returncode for p in ps])

    if returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )


def push_image(
    image: str,
    registry: Optional[str],
    namespace: Optional[str],
):
    """
    """
    title = 'Push Docker Image.'

    registry = registry + '/' if registry else ''
    namespace = namespace + '/' if namespace else ''

    cmd = ['docker', 'push', f'{registry}{namespace}{image}']

    p = run(cmd, verbose=True)

    returncode = p.returncode

    if returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )


def build_image(
    tag: List[str],
    build_arg: List[str] = None,
    dockerfile: str = 'Dockerfile',
) -> CmdFuncResult:
    """
    """
    title = 'Build Docker Image.'

    options = [
        *_parse_option(build_arg, '--build-arg'),
        *_parse_option(tag, '-t'),
    ]

    cmd = ['docker', 'build', '.', '--pull', '-f', dockerfile] + options

    p = run(cmd)

    if p.returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )
