import os
from setuptools import setup

setup(
    name='thoth-dispatcher',
    version='0.0.0',
    description='Selinon dispatcher configuration files for project Thoth',
    long_description='Selinon dispatcher configuration files for project Thoth',
    author='Fridolin Pokorny',
    author_email='fridolin@redhat.com',
    license='GPLv2+',
    packages=['thoth.dispatcher'],
    package_data={
        'thoth.dispatcher': [
            'nodes.yaml',
            os.path.join('flows', '*.yaml'),
            os.path.join('flows', '*.yml')
        ]
    },
    zip_safe=False,
)
