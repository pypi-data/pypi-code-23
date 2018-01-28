"""Unit tests for the main entry point."""
import pytest

from distutils.errors import DistutilsSetupError
from setuptools_cmmi import process_cmmi
from setuptools_cmmi.tests.cmmi_utils import cleanup_cmmi_process_test
from setuptools_cmmi.tests.cmmi_utils import setup_cmmi_process_test


def test_cmmi_process():
    """Test CMMI process."""
    try:
        temp_work_dir, dest_dir, temp_root_test_dest = setup_cmmi_process_test()

        process_cmmi(dest_dir, temp_work_dir,
                     "--prefix={0} --disable-odbc --disable-apps --disable-server --disable-pool LDFLAGS='-Wl,-rpath,parts/usr/lib -Wl,-rpath,{0}/lib'"
                     .format(dest_dir), None)

    finally:
        cleanup_cmmi_process_test(temp_work_dir, temp_root_test_dest)
        pass


def test_cmmi_failure():
    try:
        temp_work_dir, dest_dir, temp_root_test_dest = setup_cmmi_process_test()
        with pytest.raises(DistutilsSetupError):
            process_cmmi(dest_dir, temp_work_dir, "--garbage-flag", None)
    finally:
        cleanup_cmmi_process_test(temp_work_dir, temp_root_test_dest)
