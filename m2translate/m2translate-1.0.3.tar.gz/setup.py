import os
from setuptools import setup, find_packages
from pip.req import parse_requirements

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

REQUIREMENTS = [str(r.req) for r in parse_requirements('requirements.txt', session='hack')]

# grab version from GIT TAG
with open('version.txt', 'r') as ver_file:
    VERSION = ver_file.readline().strip('\n')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='m2translate',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license='MIT License',
    description='M2Translate localization / translation package',
    long_description=README,
    url='https://github.com/mdutkin/m2translate',
    author='Maxim Dutkin',
    author_email='max@dutkin.ru',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Localization'
    ],
)
