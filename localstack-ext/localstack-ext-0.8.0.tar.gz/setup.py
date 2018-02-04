#!/usr/bin/env python

import os
import re
from setuptools import find_packages, setup

install_requires = []
dependency_links = []


# root code folder
THIS_FOLDER = os.path.realpath(os.path.dirname(__file__))


# determine version
with open(os.path.join(THIS_FOLDER, 'localstack_ext', 'config.py')) as f:
    configs = f.read()
version = re.search(r'^\s*VERSION\s*=\s*[\'"](.+)[\'"]\s*$', configs, re.MULTILINE).group(1)


with open(os.path.join(THIS_FOLDER, 'requirements.txt')) as f:
    requirements = f.read()

for line in re.split('\n', requirements):
    if line and line[0] == '#' and '#egg=' in line:
        line = re.search(r'#\s*(.*)', line).group(1)
    if line and line[0] != '#':
        if '://' not in line:
            install_requires.append(line)


package_data = {
    '': ['*.md'],
    'localstack_ext': [
        'utils/*.py.enc',
        'services/*.py.enc',
        'services/cognito/*.py.enc',
        'services/ec2/*.py.enc',
        'services/iam/*.py.enc',
        'services/sts/*.py.enc'
    ]}


if __name__ == '__main__':

    setup(
        name='localstack-ext',
        version=version,
        description='Extensions for LocalStack',
        author='Waldemar Hummer',
        author_email='waldemar.hummer@gmail.com',
        url='https://github.com/localstack/localstack',
        packages=find_packages(exclude=('tests', 'tests.*')),
        package_data=package_data,
        install_requires=install_requires,
        dependency_links=dependency_links,
        test_suite='tests',
        zip_safe=False,
        classifiers=[
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'License :: OSI Approved :: Apache Software License',
            'Topic :: Software Development :: Testing',
        ]
    )
