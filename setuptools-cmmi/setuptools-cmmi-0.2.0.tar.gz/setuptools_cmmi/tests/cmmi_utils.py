import os
import uuid

import shutil
from setuptools.archive_util import unpack_archive


def setup_cmmi_process_test():
    """Setup for the CMMI processing."""
    rand_suffix = str(uuid.uuid1())

    temp_root_test_dest = os.getcwd() + "/setuptools_cmmi/tests/data/temp_test_dest-" \
                          + rand_suffix
    dest_dir = temp_root_test_dest + "/usr"
    temp_work_dir = os.getcwd() + "/setuptools_cmmi/tests/data/workdir-" + rand_suffix
    src_dist = os.getcwd() + "/setuptools_cmmi/tests/data/freetds-1.00.15.tar.gz"

    unpack_archive(src_dist, temp_work_dir)

    return temp_work_dir, dest_dir, temp_root_test_dest


def cleanup_cmmi_process_test(temp_work_dir, temp_root_test_dest):
    """Cleanup for the CMMI processing."""

    # This should already have gotten cleaned up, but just in case...
    if os.path.exists(temp_work_dir):
        shutil.rmtree(temp_work_dir)
    if os.path.exists(temp_root_test_dest):
        shutil.rmtree(temp_root_test_dest)
