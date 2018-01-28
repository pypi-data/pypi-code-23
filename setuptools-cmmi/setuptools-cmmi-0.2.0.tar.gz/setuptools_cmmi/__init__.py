import logging
import os
import sys

from distutils.errors import DistutilsSetupError

from string import Template

from datetime import datetime

import shutil
from setuptools.archive_util import unpack_archive
from setuptools_cmmi.process_cmmi import process_cmmi

if sys.version_info[0] < 3:
    import urllib as req
else:
    import urllib.request as req

LOG = logging.getLogger(__name__)
logging.basicConfig(filename='setuptools-cmmi.log',level=logging.DEBUG)

KEY_DOWNLOAD_DIR = "download_dir"
KEY_CONFIG_OPTIONS = "config_options"
KEY_CONFIG_NAME = "config_name"
KEY_URL = "url"
KEY_AUTOGEN = "autogen"
KEY_PATCH = "patch"
KEY_PATCH_OPTIONS = "patch_options"
KEY_TEMP_WORK_DIR = "temp_work_dir"
KEY_DEST_DIR = "destination_dir"
KEY_REBUILD_PACKAGES = "rebuild_packages"

VAR_PROJECT_DIR = "project_dir"
VAR_DATETIME = "datetime"

def _load_vars():
    # Load constant vars

    # Not a lot here yet, but we'll add more later.
    return {
        VAR_PROJECT_DIR: os.getcwd(),
        VAR_DATETIME: str(datetime.now())
    }


def _substitute_vars(org_values, vars):
    """Substitute variable templates in the values passed in."""
    values = {}
    for key, val in org_values.iteritems():
        if isinstance(val, list):
            new_lst = []
            for lst_val in val:
                new_lst.append(Template(lst_val).safe_substitute(vars))
            values[key] = new_lst
        else:
            values[key] = Template(val).safe_substitute(vars)
    return values


def _check_var(values, key):
    """Check for required values and throw exception if not passed."""
    val = values.get(key)
    if not val:
        raise DistutilsSetupError("Required '{}' parameter not specified for cmmi."
                                  .format(key))
    return val


def cmmi_entry_point(dist, attr, org_values):
    """Main entry point for this extension."""
    vars = _load_vars()

    values = _substitute_vars(org_values, vars)

    # Make sure all the needed vars are defined
    url = _check_var(values, KEY_URL)
    dest_dir = _check_var(values, KEY_DEST_DIR)
    temp_work_dir = values.get(KEY_TEMP_WORK_DIR,
                               vars[VAR_PROJECT_DIR] + "/temp_work_cmmi")

    try:
        config_name = values.get(KEY_CONFIG_NAME)
        config_options = values.get(KEY_CONFIG_OPTIONS, '')
        autogen = values.get(KEY_AUTOGEN, '')

        LOG.debug("dist: {}".format(dist))
        LOG.debug("attr: {}".format(attr))
        LOG.debug("url: {}".format(url))
        LOG.debug("config_name: {}".format(config_name))
        LOG.debug("config_options: {}".format(values[KEY_CONFIG_OPTIONS]))
        LOG.debug("destination_dir: {}".format(values[KEY_DEST_DIR]))

        download_unpack_file(url, temp_work_dir)

        process_cmmi(dest_dir, temp_work_dir, config_options, autogen, config_name)


    finally:
        if os.path.exists(temp_work_dir):
            shutil.rmtree(temp_work_dir)
            pass


def download_unpack_file(url, temp_work_dir):
    """Download and unpack the specified file."""
    LOG.info("Starting download for {0}".format(url))
    filehandle, _ = req.urlretrieve(url)
    unpack_archive(filehandle, temp_work_dir)
