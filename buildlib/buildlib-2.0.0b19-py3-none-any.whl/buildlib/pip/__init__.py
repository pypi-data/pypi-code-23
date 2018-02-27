"""
This module contains commands for python template engines.
"""
from cmdi import CmdResult, command
import subprocess as sp

@command
def freeze(
    sudo: bool = False,
    pip_bin: str = 'pip',
    requirements_file: str = 'requirements.txt',
    options: list = None,
    ) -> CmdResult:
    """
    Freeze current dependencies into 'requirements.txt'.
    """

    options = options or []
    sudo = 'sudo ' if sudo else ''

    if requirements_file:
        cmd: list = [sudo + pip_bin + ' freeze > ' + requirements_file + ' ' + ' '.join(options)]
    else:
        cmd: list = [sudo + pip_bin + ' freeze ' + ' '.join(options)]

    sp.run(cmd, shell=True, check=True)


@command
def install(
    package: str,
    sudo: bool = False,
    pip_bin: str = 'pip',
    options: list = None,
    ) -> CmdResult:
    """
    Run 'pip install'.
    You can define 'pip_bin' to select a pip binary for a certain environment.
    """
    options = options or []
    sudo = 'sudo ' if sudo else ''
    cmd: list = [sudo + pip_bin + ' install ' + package + ' ' + ' '.join(options)]

    sp.run(cmd, shell=True, check=True)


@command
def install_requirements(
    sudo: bool = False,
    pip_bin: str = 'pip',
    requirements_file: str = '',
    options: list = None,
    ) -> CmdResult:
    """
    Install what is listed in 'requirements.txt'.
    """
    options = options or []
    sudo = 'sudo ' if sudo else ''
    cmd: list = [sudo + pip_bin + ' install -r ' + requirements_file + ' ' + ' '.join(options)]

    sp.run(cmd, shell=True, check=True)


@command
def uninstall(
    package: str,
    sudo: bool = False,
    pip_bin: str = 'pip',
    options: list = None,
    ) -> CmdResult:
    """
    Run 'pip uninstall'.
    You can define 'pip_bin' to select a pip binary for a certain environment.
    """
    options = options or []
    sudo = 'sudo ' if sudo else ''
    cmd: list = [sudo + pip_bin + ' uninstall ' + package + ' ' + ' '.join(options)]

    sp.run(cmd, shell=True, check=True)


