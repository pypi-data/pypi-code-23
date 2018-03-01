#!/usr/bin/env python3
"""Install coop"""

from setuptools import find_packages, setup

with open('coop/_version.py', 'r') as f:
    version = None
    exec(f.read())

with open('README.rst', 'r') as f:
    readme = f.read()


install_requires = ['wagtail>=2.0']

setup(
    name='coop',
    version=version,
    description='Standard base to build Wagtail sites from',
    long_description=readme,
    author='Takeflight',
    author_email='developers@takeflight.com.au',
    url='https://gitlab.com/takeflight/coop',

    install_requires=[
        'psycopg2==2.6.1',
        'wagtail~=2.0',
        'django~=1.11.0',
        'pytz>=0',
        'Jinja2~=2.10.0',
        'wagtail-metadata~=2.0',
        'wagtail-accessibility~=0.1.1',
        'wagtailfontawesome~=1.0',
        'requests>=2.10.0,<3',
        'elasticsearch~=2.0',
        'bugsnag~=3.0',
    ],

    zip_safe=False,
    license='BSD License',

    packages=find_packages(exclude=['tests*']),

    include_package_data=True,
    package_data={},

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
