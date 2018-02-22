import setuptools
import sys


def is_python_version_supported():
    if not sys.version_info.major >= 3:
        print('This package requires Python 3.x or higher')
        sys.exit(1)


def is_setuptools_version_supported():
    major, minor, patch = setuptools.__version__.split('.')
    if int(major) < 32:
        print('This package requires setuptools >= 32.0.0')
        sys.exit(2)


# Make sure this package has the requirements to install
is_python_version_supported()
is_setuptools_version_supported()

# Run setuptools.setup(), the setting values are in the setup.cfg file
setuptools.setup()
