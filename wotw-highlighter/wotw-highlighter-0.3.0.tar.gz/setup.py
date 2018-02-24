from os.path import join
from setuptools import setup, find_packages

with open(join('wotw_highlighter', 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

setup(
    name='wotw-highlighter',
    version=__version__,
    packages=find_packages(),
    package_data={
        '': [
            'VERSION',
            'data/*.css'
        ]
    },
    include_package_data=True
)
