#!/usr/bin/env python

from setuptools import find_packages, setup


requirements = [

    'click>=6.7',
    'mysqlclient>=1.3.12',
    'numpy>=1.14.0',
    'pandas>=0.22.0',
    'pydataset>=0.2.0',
    'python-dateutil>=2.6.1',
    'pytz>=2018.3',
    'six>=1.11.0',
    'SQLAlchemy>=1.2.2',

]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
]

setup(
    name='autoalchemy',
    version='0.1.0',
    description="Push raw data files to a SQL database by automatically generating a schema, with sane typing and naming.",
    author="Eric Chang",
    author_email='ericchang00@gmail.com',
    url='https://github.com/ericchang00/autoalchemy',
    packages=find_packages(include=['autoalchemy']),
    entry_points={
        'console_scripts': [
            'autoalchemy=autoalchemy.cli:cli'
        ]
    },
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='autoalchemy',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests.py',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
