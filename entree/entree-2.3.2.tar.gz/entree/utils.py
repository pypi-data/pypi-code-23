#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. module:: entree.utils
.. moduleauthor:: Julien Spronck
.. created:: Feb 2018

Simple module to create files and directories in a programming project
"""
import fnmatch
import json
import os
import time
import zipfile

import six
from jinja2 import Template

CONFIG_FILE_NAME = 'entree_config.json'
CONFIG_DIR = ''


def get_config_dir():
    '''Returns path for the config directory.
    '''
    if CONFIG_DIR:
        return CONFIG_DIR
    username = os.getenv("SUDO_USER") or os.getenv("USER")
    homedir = os.path.expanduser('~'+username)
    return os.path.join(homedir, ".config")


def get_config_file():
    '''Returns path of the config file.
    '''
    configdir = get_config_dir()
    configfile = os.path.join(configdir, CONFIG_FILE_NAME)
    return configfile


def read_config():
    '''Reads the config file

    Returns:
        config: dict containing the configuration
    '''
    configfile = get_config_file()
    if not os.path.exists(configfile):
        set_config()
    with open(configfile) as fil:
        return json.load(fil)


def get_config_param(param, value=None, project_type=None):
    '''Gets a specific parameter from the config file

    Args:
        param: the name of the parameter to get from the config file

    Keyword Args:
        value (default=None): default value for the parameter if not found
            in the config file
        project_type (str, default=None): project type for project-specific
            configuration

    Returns:
        config parameter
    '''
    config = read_config()
    if (project_type and 'project_config' in config and
            project_type in config['project_config']):
        project = config['project_config'][project_type]
        if param in project:
            return project[param]
        return value
    if param in config:
        return config[param]
    return value


def set_config(overwrite=False, **config):
    '''Sets the config parameters

    Keyword Args:
        overwrite (bool, default=False): Set to True to overwrite an existing
            config file.
        **config: all other keyword args will be used
            as config parameters in the config file.
    '''
    if 'author' not in config:
        config['author'] = '<UNDEFINED>'
    if 'author_email_prefix' not in config:
        config['author_email_prefix'] = '<UNDEFINED>'
    if 'author_email_suffix' not in config:
        config['author_email_suffix'] = '<UNDEFINED>'
    if 'author_url' not in config:
        config['author_url'] = '<UNDEFINED>'
    configdir = get_config_dir()
    if not os.path.exists(configdir):
        os.makedirs(configdir)
    configfile = os.path.join(configdir, CONFIG_FILE_NAME)
    if not os.path.exists(configfile) or overwrite:
        with open(configfile, 'w') as fil:
            json.dump(config, fil, indent=4, sort_keys=True)


def create_general_file(fname, file_content, zipf=None):
    '''Creates a file.

    Args:
        fname (str): file name
        file_content (iterator): generator/iterator containing
            the file content.

    Keyword args:
        zipf (zipfile.ZipFile, default=None)
    '''

    # if dirname and not os.path.exists(dirname):
    #     os.makedirs(dirname)
    if zipf is None:
        if os.path.exists(fname):
            raise IOError('File already exists. Will not overwrite')
        with open(fname, 'w') as fil:
            for line in file_content:
                fil.write(line)
    else:
        data = zipfile.ZipInfo(fname)
        data.date_time = time.localtime(time.time())[:6]
        data.compress_type = zipfile.ZIP_DEFLATED
        zipf.writestr(data, file_content)


def create_dirs(rootdir, *dirs):
    '''
    Creates directories

    Args:
        rootdir (str): the root directory
        dirs (str): directories to create
    '''
    if not os.path.exists(rootdir):
        raise IOError('Root directory not found: "'+rootdir+'"')

    for thedir in dirs:
        if not os.path.exists(thedir):
            os.makedirs(thedir)


def render_template(filename, **kwargs):
    '''Renders a template file given the variables defined in kwargs

    Args:
        filename (str): the filename

    Keyword args:
        **kwargs: dictionary containing the variables needed in the template

    Returns:
        string containing the content of the file after templating
    '''
    with open(filename) as fil:
        template = Template(fil.read())

    return template.render(**kwargs)


def copy_file_structure(rootdir, path, replace=None, files_to_ignore=None,
                        partial=None, zipf=None, template_root=None,
                        **kwargs):
    '''Walks through the file structure and copy all directories and files.

    Args:
        rootdir (str): the root directory where the files will be copied to
        path (str): the path to walk through and reproduce

    Keyword args:
        replace (dict, default=None): dictionary for file name replacement.
            Keys are old file names and values are new file names.
        files_to_ignore (list, default=None): list of file names to ignore.
        partial (list, default=None): list of paths for a partial build.
            Only the paths in the lists will be created.
        zipf (zipfile.ZipFile, default=None)
        template_root (str, default=None): the path to the project template
        directory
        **kwargs: dictionary containing the variables for templating
    '''
    if not os.path.exists(rootdir) and zipf is None:
        raise IOError('Root directory not found: "'+rootdir+'"')

    if not files_to_ignore:
        files_to_ignore = get_config_param('files_to_ignore', [])

    if template_root is None:
        template_root = path

    for fname in os.listdir(path):
        src = os.path.join(path, fname)
        relpath = os.path.relpath(src, start=template_root)
        if partial and src not in partial:
            # Partial build: only files and dirs in the partial list
            # will be created
            continue
        ignoring = False
        for pat in files_to_ignore:
            if (fnmatch.fnmatch(fname, pat) or
                    fnmatch.fnmatch(relpath, pat)):
                ignoring = True
                break
        if ignoring:
            # file path is in the list of files to ignore
            six.print_('File ignored: `{0}`'.format(src))
            continue
        if replace and fname in replace:
            fname = Template(replace[fname]).render(**kwargs)
        elif fname.endswith('_py.template'):
            fname = fname[:-12]+'.py'

        dst = os.path.join(rootdir, fname)
        if os.path.isdir(src):
            if not os.path.exists(dst) and zipf is None:
                os.makedirs(dst)
            copy_file_structure(dst, src, replace=replace, partial=partial,
                                files_to_ignore=files_to_ignore, zipf=zipf,
                                template_root=template_root,
                                **kwargs)
        elif os.path.isfile(src):
            file_content = render_template(src, **kwargs)
            create_general_file(dst, file_content, zipf=zipf)


def create_single_file(rootdir, newfilename, template_path, zipf=None,
                       **kwargs):
    '''Creates a single file from a template.

    Args:
        rootdir (str): the root directory where the file will be created
        newfilename (str): name of the new file
        template_path (str): the path for the template file

    Keyword args:
        zipf (zipfile.ZipFile, default=None)
        **kwargs: dictionary containing the variables for templating
    '''
    if not os.path.exists(rootdir):
        raise IOError('Root directory not found: "'+rootdir+'"')

    file_content = render_template(template_path, **kwargs)

    dst = os.path.join(rootdir, newfilename)

    create_general_file(dst, file_content, zipf=zipf)


def get_all_dirs_and_files(rootdir, basename='', files_to_ignore=None):
    '''Get all path names for template directories
    '''
    dirs = []
    files = []

    if files_to_ignore is None:
        files_to_ignore = get_config_param('files_to_ignore', [])

    for fname in os.listdir(rootdir):
        subpath = os.path.join(rootdir, fname)
        newbasename = os.path.join(basename, fname)
        ignoring = False
        for pat in files_to_ignore:
            if (fnmatch.fnmatch(fname, pat) or
                    fnmatch.fnmatch(newbasename, pat)):
                ignoring = True
                break
        if ignoring:
            continue
        if os.path.isdir(subpath):
            dirs.append(newbasename)
            newdirs, newfiles = get_all_dirs_and_files(
                subpath,
                basename=newbasename,
                files_to_ignore=files_to_ignore
            )
            dirs += newdirs
            files += newfiles
        elif os.path.isfile(subpath):
            files.append(newbasename)
    return dirs, files


def replace_pathname(pathname, replace=None, **kwargs):
    '''Replaces a directory name based on patterns defined in a dictionary

    Args:
        replace (dict, default=None): dictionary with replacement patterns

    Returns:
        new directory name (str)
    '''
    if not replace:
        if pathname.endswith('_py.template'):
            return pathname[:-12]+'.py'
        return pathname

    dirsplit = pathname.split(os.sep)
    if len(dirsplit) > 1:
        # Apply this function to all directory names in the path
        dirsplit = [replace_pathname(dname, replace=replace, **kwargs)
                    for dname in dirsplit]
        return os.path.join(*dirsplit)
    else:
        if pathname in replace:
            template = Template(replace[pathname])
            return template.render(**kwargs)
        if pathname.endswith('_py.template'):
            return pathname[:-12]+'.py'
        # No match in `replace` => returns the orginal name
        return pathname


def filemap(files, replace=None, **kwargs):
    '''Mapping between file/dir names and their template
    for testing purposes.
    '''
    return {name: replace_pathname(name, replace=replace, **kwargs)
            for name in files}
