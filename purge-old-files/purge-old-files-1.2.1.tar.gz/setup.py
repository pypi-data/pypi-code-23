from os.path import join, dirname, abspath

from setuptools import setup, find_packages


def read(filename):
    with open(abspath(join(dirname(__file__), filename))) as fileobj:
        return fileobj.read()


def get_version(package):
    return [
        line for line in read('{}/__init__.py'.format(package)).splitlines()
        if line.startswith('__version__ = ')][0].split("'")[1]


NAME = 'purge-old-files'
PACKAGE = NAME.replace('-', '_')
VERSION = get_version(PACKAGE)


setup(
    name=NAME,
    version=VERSION,
    description='Purge old files using constraints',
    long_description=read('README.rst'),
    packages=find_packages(),
    author='Philippe Muller',
    author_email='philippe.muller@gmail.com',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: POSIX :: Linux',
    ],
    url='https://github.com/pmuller/purge-old-files',
    license='Apache License 2.0',
    entry_points="""
        [console_scripts]
        purge-old-files = purge_old_files.cli:main
    """,
)
