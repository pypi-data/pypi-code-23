# coding: utf-8

import subprocess

import logging
logger = logging.getLogger(__name__)


def run(cmd, wait=True, *args, **kwargs):
    process = subprocess.Popen(cmd, *args, **kwargs)
    if wait:
        stdout, stderr = process.communicate()
        return process.returncode, stdout
    else:
        return process
