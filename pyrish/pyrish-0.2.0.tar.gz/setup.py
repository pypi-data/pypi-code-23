#!/usr/bin/env python

from pip.req import parse_requirements
from setuptools import setup, find_packages


def read(_file):
    with open(_file) as f:
        content = f.read()
    return content


def iter_requirements(_file):
    requirements = parse_requirements(_file, session=False)
    return [str(r.req) for r in requirements]


readme = read('README.rst')
history = read('HISTORY.rst')

requirements = iter_requirements('requirements/prod.lock')
setup_requirements = ('pytest-runner',)
test_requirements = iter_requirements('requirements/dev.lock')

classifiers = (
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.6'
)

setup(
    name='pyrish',
    version='0.2.0',
    description="A growing collection of code and utility classes.",
    long_description=f"{readme}\n\n{history}",
    author="Dhia Abbassi",
    author_email='contact@dhia.io',
    url='https://github.com/dhiatn/pyrish',
    packages=find_packages(include=['pyrish']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pyrish',
    classifiers=classifiers,
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
