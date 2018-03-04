#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_template.command_template import CommandTemplate


CHANGE_PATH = CommandTemplate("cd {path}")
MAKE_DIRECTORY = CommandTemplate("mkdir -p {path}")
FILE_INFO = CommandTemplate("file {file_path}")
UNTAR_GZ_PACKAGE = CommandTemplate("tar -xvzf {trex_package} | sed -e 's@/.*@@' | uniq")
UNTAR_PACKAGE = CommandTemplate("tar -xvf {trex_package} | sed -e 's@/.*@@' | uniq")
CHECK_PATH_EXISTENCE = CommandTemplate("ls {path}")
CREATE_SIM_LINK = CommandTemplate("ln -s {source_path} {link_name}")
MOVE_FILE = CommandTemplate("mv -f {source_path} {dest_path}")
DOWNLOAD_FILE = CommandTemplate("wget -O {file_name} {url}")
