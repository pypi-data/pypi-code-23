#!/usr/bin/env python3
# encoding: utf-8

"""
cessa.docker
============

This module encapsulates some docker commands.

:Copyright (c) by hac(Xiao An) <hac@zju.edu.cn>. All Rights Reserved.

"""

import subprocess

def ls_images(all_=False, quiet=False, display=False, no_trunc=False):
    """ lists Docker images

    :all_: show all images or not(default hides intermediate images)
    :quiet: only show numeric IDs or not
    :display: display to stdout or not
    :no_trunc: don't truncate output
    :returns: image list

    """
    cmd = ['docker', 'images']
    if all_: cmd.append('-a')
    if quiet: cmd.append('-q')
    if no_trunc: cmd.append('--no-trunc')
    out = None if display else subprocess.PIPE
    p = subprocess.run(cmd,
                       stdout = out,
                       stderr = out,
                       universal_newlines=True)
    return (p.stdout, None) if p.returncode == 0 else (None, p.stderr)

def ls_containers(all_=False, quiet=False, no_trunc=False, filters=None, display=False):
    """ lists Docker containers

    :all_: show all containers or not(default shows just running)
    :quiet: only show numeric IDs or not
    :no_trunc: don't truncate output
    :filters: filter output based on conditions provided
    :display: display to stdout or not
    :returns: container list

    """
    cmd = ['docker', 'ps']
    if all_: cmd.append('-a')
    if quiet: cmd.append('-q')
    if no_trunc: cmd.append('--no-trunc')
    if filters != None: cmd += ['-f', filters]
    out = None if display else subprocess.PIPE
    p = subprocess.run(cmd,
                       stdout = out,
                       stderr = out,
                       universal_newlines=True)
    return (p.stdout, None) if p.returncode == 0 else (None, p.stderr)

def query_image(image_id):
    """ query image by its ID

    :image_id: image ID
    :returns: image ID if exists, or None

    """
    image_list, err = ls_images(quiet=True)
    if image_list == None:
        return None
    return image_id if image_id in image_list else None


def query_container(name):
    """ query container ID by its name

    :name: container name
    :returns: container ID if exists, or None

    """
    out, _ = ls_containers(all_=True, quiet=True, filters='name={}'.format(name))
    return None if out == '' else out
