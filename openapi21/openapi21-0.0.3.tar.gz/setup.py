#!/usr/bin/env python3

from setuptools import setup, find_packages

import os.path

root_dir = os.path.dirname(os.path.abspath(__file__))
version_f = open(os.path.join(root_dir, 'openapi21/version.py'))
install_requires = [
    'jsonschema>=2.6.0',
    'swagger_spec_validator>=2.1.0',
    'PyYAML>=3.12'
]
tests_require = [
    'pytest',
    'pytest-cov'
]
setup_requires = [
    'pytest-runner',
    'flake8'
]
version = {}

exec(version_f.read(), version)
version = version['VERSION']


setup(
    name='openapi21',
    packages=find_packages(),
    include_package_data=True,
    version=version,
    description='An Unofficial OpenAPI 2.1 Specification Python Validator',
    author='Diogo Dutra',
    author_email='dutradda@gmail.com',
    url='https://github.com/dutradda/openapi21-python',
    keywords='openapi oai swagger rest api validator validation',
    license='MIT',
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Topic :: Text Processing'
    ]
)
