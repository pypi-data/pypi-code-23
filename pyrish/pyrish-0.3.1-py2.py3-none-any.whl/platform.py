"""
This module tries to provide a ready to consume data that identifies the system as
much as possible. It makes this information available via function APIs.
"""

__all__ = (
    'architecture',
    'cpu_info',
    'cpu_model_name',
    'disk_usage',
    'host_info',
    'internal_ip',
    'is_linux',
    'is_osx',
    'is_win',
    'os_info',
    'os_name',
    'os_release',
    'uptime',
    'virtual_memory_usage',
    '_cpu_linux_model',
    '_cpu_osx_model'
)

import platform
import socket
import time
from typing import Dict, Any

import humanfriendly as hf
import psutil

from ._globals import (LINUX, OSX, WINDOWS, SYS_PATH, PUBLIC_DNS,
                       CPU_MODEL_LINUX_CMD, CPU_MODEL_OSX_CMD, LOCALHOST)
from .shell import run_shell


def os_name() -> str:
    """Returns the OS name, e.g. 'Linux', 'Darwin' etc.
    An empty string is returned if the value cannot be determined.
    """
    return platform.system()


def is_linux() -> bool:
    """Checks if it's a Linux environment

    :return: (bool)
    """
    return os_name() == LINUX


def is_osx() -> bool:
    """Checks if it's OSX environment

    :return: (bool)
    """
    return os_name() == OSX


def is_win() -> bool:
    """Checks if it's Windows environment

    :return: (bool)
    """
    return os_name() == WINDOWS


def os_release() -> str:
    """
    Returns the release version of the os. An empty string is returned
    if the value cannot be determined.

    :return: (str)

    Usage::

        >>> os_release()
        '17.3.0'
    """
    return platform.release()


def architecture() -> str:
    """Returns the system's bit architecture

    Usage::

        >>> architecture()
        '64bit'
    """

    arch, _ = platform.architecture()
    return arch


def os_info() -> Dict[str, str]:
    """Collects information about the installed operating system.

    :return: (Dict[str, str])

    Usage::

        >>> os_info()
        {
            'arch': '64bit',
            'name': 'Darwin',
            'release': '17.3.0',
        }
    """

    info = {
        'name': os_name(),
        'release': os_release(),
        'arch': architecture()
    }
    return info


def uptime(human: bool = False) -> Any:
    """Gives the time since then the system has been working and available.
    The time is returned in seconds. If ``human=True`` uptime
    will be returned as a human readable string.

    :param (bool) human: convert time to human readable sting
    :return: (str/float)

    Usage::

        >>> uptime()
        93222.41144919395
        >>> uptime(human=True)
        '1 day, 1 hour and 54 minutes'
    """

    now = time.time()
    uptime = psutil.boot_time()
    uptime_delta = now - uptime
    if human:
        uptime_delta = hf.format_timespan(uptime_delta)
    return uptime_delta


def virtual_memory_usage(human: bool = False) -> Dict[str, Any]:
    """Return statistics about system memory usage

    :param (bool) human: convert memory size to human readable sting
    :return: (Dict[str, Any])

    Usage::

        >>> virtual_memory_usage(human=True)
        {
            'free': '1.03 GB',
            'total': '17.18 GB',
            'usage_percent': 73.5,
            'used': '14.71 GB'
        }
    """

    info = {}
    memory = psutil.virtual_memory()
    info['total'] = memory.total
    info['used'] = memory.used
    info['free'] = memory.free
    if human:
        info = {k: hf.format_size(v) for k, v in info.items()}
    info['usage_percent'] = memory.percent
    return info


def disk_usage(human: bool = False) -> Dict[str, Any]:
    """Return disk usage statistics

    :param (bool) human: convert memory size to human readable sting
    :return: (Dict[str, Any])

    Usage::

        >>> disk_usage(human=True)
        {
            'free': '459.3 GB',
            'total': '499.96 GB',
            'usage_percent': 7.4,
            'used': '36.75 GB'
        }
    """

    info = {}
    memory = psutil.disk_usage(SYS_PATH)
    info['total'] = memory.total
    info['used'] = memory.used
    info['free'] = memory.free
    if human:
        info = {k: hf.format_size(v) for k, v in info.items()}
    info['usage_percent'] = memory.percent
    return info


def cpu_info(include_logical=False) -> Dict[str, Any]:
    """Returns number of CPU physical [logical] cores and model.

    :return: Dict[str, str]

    Usage::

        >>> cpu_info()
        {
            'cores': 4,
            'model_name': 'Intel(R) Core(TM) i7-7700HQ CPU @ 2.80GHz'
        }
    """

    info = {}
    info['cores'] = psutil.cpu_count(logical=include_logical)
    info['model_name'] = cpu_model_name()
    return info


def _cpu_linux_model():
    """Grabs CPU brand description from a Linux environment"""

    model = run_shell(CPU_MODEL_LINUX_CMD)
    return model


def _cpu_osx_model():
    """Grabs CPU brand description from a OSX environment"""

    model = run_shell(CPU_MODEL_OSX_CMD)
    return model


def cpu_model_name() -> str:
    """Returns CPU brand description that gives
    an overview of the CPU family, model.

    :return: (str)

    Usage::

        >>> cpu_model_name()
        'Intel(R) Core(TM) i7-7700HQ CPU @ 2.80GHz'
    """

    if is_linux():
        return _cpu_linux_model()
    if is_osx():
        return _cpu_osx_model()
    return platform.processor()


def internal_ip() -> str:
    """Return the internal ip address of the host.

    Usage::

        >>> internal_ip()
        '192.168.102.55'
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((PUBLIC_DNS, 80))
        ip = s.getsockname()[0]
        s.close()
    except OSError as _:
        ip = LOCALHOST
    return ip


def host_info(human: bool = False) -> Dict[str, Any]:
    """ Return a collection of information about server and it's current state.

    :param (bool) human: convert all data to human readable sting
    :return:

    Usage::

        >>> host_info()
        {
            'cpu': {
                'cores': 4,
                'model_name': 'Intel(R) Core(TM) i7-7700HQ CPU @ 2.80GHz'
            },
            'disk': {
                'free': 459298390016,
                'total': 499963170816,
                'usage_percent': 7.4,
                'used': 36753997824
            },
            'os': {
                'arch': '64bit',
                'name': 'Darwin',
                'release': '17.3.0',
            },
            'private_ip': '192.168.102.55',
            'uptime': 93222.41144919395,
            'virtual_memory': {
                'free': 1020211200,
                'total': 17179869184,
                'usage_percent': 73.5,
                'used': 14719655936
            }
        }
        >>> host_info(human=True)
        {
            'cpu': {
                'cores': 4,
                'model_name': 'Intel(R) Core(TM) i7-7700HQ CPU @ 2.80GHz'
            },
            'disk': {
                'free': '459.3 GB',
                'total': '499.96 GB',
                'usage_percent': 7.4,
                'used': '36.75 GB'
            },
            'os': {
                'arch': '64bit',
                'name': 'Darwin',
                'release': '17.3.0',
            },
            'private_ip': '192.168.102.55',
            'uptime': '1 day, 1 hour and 54 minutes',
            'virtual_memory': {
                'free': '1.03 GB',
                'total': '17.18 GB',
                'usage_percent': 73.5,
                'used': '14.71 GB'
            }
        }
    """

    info = {}
    info['os'] = os_info()
    info['uptime'] = uptime(human)
    info['virtual_memory'] = virtual_memory_usage(human)
    info['disk'] = disk_usage(human)
    info['cpu'] = cpu_info()
    info['private_ip'] = internal_ip()

    return info
