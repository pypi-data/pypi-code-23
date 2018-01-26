import os
import sys
from setuptools import setup, find_packages

PACKAGE_NAME = 'd3m_metadata'
MINIMUM_PYTHON_VERSION = 3, 6


def check_python_version():
    """Exit when the Python version is too low."""
    if sys.version_info < MINIMUM_PYTHON_VERSION:
        sys.exit("Python {}.{}+ is required.".format(*MINIMUM_PYTHON_VERSION))


def read_package_variable(key):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join(PACKAGE_NAME, '__init__.py')
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(' ')
            if parts and parts[0] == key:
                return parts[-1].strip("'")
    assert False, "'{0}' not found in '{1}'".format(key, module_path)


check_python_version()
version = read_package_variable('__version__')

setup(
    name=PACKAGE_NAME,
    version=version,
    description='Metadata for values and primitives',
    author='DARPA D3M Program',
    packages=find_packages(exclude=['contrib', 'docs', 'site', 'tests*']),
    package_data={'d3m_metadata': ['schemas/*/*.json']},
    install_requires=[
        'scikit-learn[alldeps]==0.19.1',
        'pytypes==1.0b3.post19',
        'frozendict==1.2',
        'numpy==1.14',
        'jsonschema==2.6.0',
        'requests==2.18.4',
        'strict-rfc3339==0.7',
        'rfc3987==1.3.7',
        'webcolors==1.7',
        'dateparser==0.6.0',
        'pandas==0.22',
        'networkx==2.0',
        'typing-inspect==0.2.0',
        'GitPython==2.1.8',
        'jsonpath-ng==1.4.3',
    ],
    dependency_links=[
        'git+https://github.com/Stewori/pytypes.git@2f1b6d293448805cc350737945a140115b5f5981#egg=pytypes-1.0b3.post19',
    ],
    url='https://gitlab.com/datadrivendiscovery/metadata',
)
