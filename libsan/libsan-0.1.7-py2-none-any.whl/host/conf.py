# Copyright (C) 2016 Red Hat, Inc.
# This file is part of libsan.
#
# libsan is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libsan is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with libsan.  If not, see <http://www.gnu.org/licenses/>.

"""conf.py: Module to SAN config file."""

__author__      = "Bruno Goncalves"
__copyright__   = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import ConfigParser
import os
import re
import json

def _print(string):
    module_name = __name__
    string = re.sub("FAIL:", "FAIL:("+ module_name + ")", string)
    string = re.sub("FATAL:", "FATAL:("+ module_name + ")", string)
    string = re.sub("WARN:", "WARN:("+ module_name + ")", string)
    string = re.sub("DEBUG:", "DEBUG:("+ module_name + ")", string)
    print string
    return


def load_config(config_file):
    """
    Read a conf file
    The arguments are:
    \tconfig_file:         Full path to file where is the config
    Returns:
    \\tDict:            A dict with all config
    """
    if not os.path.isfile(config_file):
        _print("FAIL: Could not read %s" % config_file)
        return None

    #config = ConfigParser.ConfigParser()
    #We want to preserve case
    #config.optionxform=str
    #config.read(config_file)

    #class_name_dict = {}
    #class_name_dict["switch"] = "libsan.switch"
    #class_name_dict["array"] = "libsan.array"
    #class_name_dict["pyswitch"] = "libsan.physwitch"

    config_dict = []

    #for section in config.sections():
    #    section_dict = {}
    #    section_dict["name"] = section
    #    section_dict["options"] = {}
    #    for option in config.options(section):
    #        sec_key = option
    #        #remove FC port prefix
    #        #sec_key = re.sub("^wwpn-", "", sec_key)
    #        value = config.get(section, option)
    #        #we need to trail comments out
    #        value = re.sub("#.*", "", value)
    #        value = value.strip()
    #        section_dict["options"][sec_key] = value
    #    config_dict.append(section_dict)

    #Not using ConfigParser as we would like to have repeated sections
    try:
        f = open(config_file, 'r')
        config_output = f.read()
        f.close()
    except:
        _print("FAIL: load_config() - Could not read %s" % config_file)
        return None

    lines = config_output.split("\n")
    blank_line = re.compile("\s+")
    comment_regex = re.compile(".*(#.*)$")
    section_regex = re.compile("\s*\[(.*)\]")
    option_regex = re.compile("\s*(\S+)\s*=\s*(.*)$")

    current_section = None
    sec_dict = None
    for line in lines:
        actual_line = line
        m = comment_regex.match(line)
        if m:
            #remove comment
            actual_line = actual_line.replace(m.group(1), "")
        if blank_line.match(actual_line):
            continue
        #Check if it is a section
        m = section_regex.match(actual_line)
        if m:
            #New section
            if current_section:
                #add previous section to config_dict
                config_dict.append(sec_dict)
            current_section = actual_line
            #creating new section data
            sec_dict = {}
            sec_dict["name"] = m.group(1)
            sec_dict["options"] = {}
            continue
        #Check if it is option of section
        m = option_regex.match(actual_line)
        if m:
            if not current_section:
                _print("FAIL: load_config() - option (%s) does not belong to any section" % line)
                return None
            #Store the value removing trailing spaces
            sec_dict["options"][m.group(1)] = m.group(2).strip()
    #add last section to config_dict
    if sec_dict:
         config_dict.append(sec_dict)
    return config_dict


def config_add_entry(config_key, config_param, param_value, config_file):
    """
    Add entry to a config file
    The arguments are:
    \tconfig_key:           Key register that we will add the entry
    \tconfig_param:         The config parameter that will be added
    \tconfig_value:         The value for the parameter
    \tconfig_file:          Full path to file where is the config
    Returns:
        True
        or
        False
    """

    if not os.path.isfile(config_file):
        _print("FAIL: config_add_entry() - Could not open %s" % config_file)
        return None

    config = ConfigParser.ConfigParser()
    #We want to preserve case
    config.optionxform=str
    config.read(config_file)

    config.set(config_key, config_param, param_value)

    with open(config_file, 'w') as configfile:
        config.write(configfile)

    return True


def config_remove_entry(config_key, config_param, config_file):
    """
    Remove entry from a config file
    The arguments are:
    \tconfig_key:           Key register that we will add the entry
    \tconfig_param:         The config parameter that will be added
    \tconfig_file:          Full path to file where is the config
    Returns:
        True
        or
        False
    """

    if not os.path.isfile(config_file):
        _print("FAIL: config_add_entry() - Could not open %s" % config_file)
        return None

    config = ConfigParser.ConfigParser()
    #We want to preserve case
    config.optionxform=str
    config.read(config_file)

    config.remove_option(config_key, config_param)

    with open(config_file, 'w') as configfile:
        config.write(configfile)

    return True


def get_alias(config_dict, value):
    """
    Given a value get its alias if exist.
    The arguments are:
    \tconfig_dict:        The config dict return by load_config
    \tvalue:              The value we want get the alias from
    Returns:
    \tString:             The alias
    \tNone:               There was a problem or alias does not exist
    """
    if "alias" not in config_dict.keys():
        return None

    for alias in config_dict["alias"].keys():
        if config_dict["alias"][alias] == value:
            return alias
    return None

