# -*- coding: utf8 -*-
import sys
import logging
import threading
from missinglink.pip_util import pip_install
import pkg_resources
from pkg_resources import VersionConflict, DistributionNotFound


COMMON_DEPENDENCIES = [
    'ply==3.10',
    'flatten_json==0.1.6',
    'tqdm>=4.19,<5.0',
    'pyparsing==2.2.0',
    'pyjwt>=1.5.2',
    'retrying>=1.3.3',
    'google-cloud-core>=0.28.0,<0.29.0',
    'requests_cache>=0.4.13',
    'diskcache>=3.0.1',
    'scandir>=1.6',
]

GCS_DEPENDENCIES = [
    'google-cloud-storage==1.6.0',
]
S3_DEPENDENCIES = [
    'boto3>=1.4.8,<1.5.0',
]

KEYWORDS = []


__pip_install_lock = threading.Lock()


def install_dependencies(dependencies, throw_exception=True):
    running_under_virtualenv = getattr(sys, 'real_prefix', None) is not None

    needed_dependencies = []
    for requirement in dependencies:
        if _is_dependency_installed(requirement):
            continue

        needed_dependencies += [requirement]

    if not needed_dependencies:
        return

    with __pip_install_lock:
        p, args = pip_install(None, needed_dependencies, not running_under_virtualenv)

        if p is None:
            raise Exception('Failed to install requirement: %s' % needed_dependencies)

        try:
            std_output, std_err = p.communicate()
        except Exception:
            if throw_exception:
                raise

            logging.exception('%s failed', ' '.join(args))
            return False

        rc = p.returncode

        if rc == 0:
            logging.info('install requirement: %s' % needed_dependencies)
            logging.info('ran %s (%s)\n%s\n%s', ' '.join(args), rc, std_err, std_output)
        else:
            logging.error('Failed to install requirement: %s' % needed_dependencies)
            logging.error('Failed to run %s (%s)\n%s\n%s', ' '.join(args), rc, std_err, std_output)

            if throw_exception:
                raise Exception('Failed to install requirement: %s' % needed_dependencies)


def _is_dependency_installed(requirement):
    try:
        pkg_resources.require(requirement)
    except (IOError, DistributionNotFound, VersionConflict):
        return False

    return True
