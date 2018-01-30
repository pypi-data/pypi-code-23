#!/usr/bin/env python
# -*- coding: utf-8 -*-
import versioneer
from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pytest>=3.0.4',
    'pyyaml',
    'snakemake>=3.10.0',
    'rst2ansi',
    'pygments',
    'sphinx-rtd-theme',
    'versioneer',
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
    'pytest-runner',
    'pyyaml',
    'snakemake',
]

scripts = ['scripts/deploy_workflow.py']

setup(
    name='lts_workflows',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="SciLifeLab long-term support workflows",
    long_description=readme + '\n\n' + history,
    author="Per Unneberg",
    author_email='per.unneberg@scilifelab.se',
    url='https://bitbucket.org/scilifelab-lts/lts-workflows',
    scripts=scripts,
    packages=[
        'lts_workflows',
        'lts_workflows.pytest',
        'lts_workflows.snakemake',
    ],
    package_dir={'lts_workflows':
                 'lts_workflows'},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='lts_workflows',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={'pytest11': ['lts_workflows = lts_workflows.pytest.plugin']},
)
