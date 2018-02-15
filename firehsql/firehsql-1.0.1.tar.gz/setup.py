from setuptools import setup, find_packages

RELEASE_VERSION = '1.0.1'

setup(
    name='firehsql',
    version=RELEASE_VERSION,
    url='https://github.com/dozymoe/firehsql',
    download_url='https://github.com/dozymoe/firehsql/tarball/' +\
            RELEASE_VERSION,

    author='Fahri Reza',
    author_email='dozymoe@gmail.com',
    description='Simple SQL generator.',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    platforms='any',
    license='GPLv3',
)
