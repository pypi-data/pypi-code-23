import shutil
import os
import re


def version():
    """Function returns most recent visualization package version"""

    search_path = os.path.dirname(os.path.abspath(__file__))
    subdirs = [name for name in os.listdir(search_path) if os.path.isdir(os.path.join(search_path, name))]
    versions = [re.findall('\d+', subdir) for subdir in subdirs]

    return str(max(versions)[0])


def copy(vispack_destination, vispack_version=None):
    """
    Function to copy a version of the visualization package to a new destination.

    :param vispack_destination: name of the folder to put the visualization package
    :type vispack_destination: basestring
    :param vispack_version: version of the visualization package in yymmdd format
    :type vispack_version: basestring, None
    :return: folder with visualization package
    :rtype: file
    """

    # Get vispack version
    if vispack_version is None:
        vispack_version = version()

    # Get directory name of the vispack
    vispack_folder = 'VISTOMS_' + vispack_version

    # Get path names
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), vispack_folder)
    dst = os.path.abspath(vispack_destination)

    # Remove destination directory and copy files
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    return
