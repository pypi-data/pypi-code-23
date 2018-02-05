#!/usr/bin/env python
"""Setup script for Matchlight SDK."""
import io
import os
import sys

import setuptools


def setup():  # noqa: D103
    needs_sphinx = {'build_sphinx', 'upload_docs'}.intersection(sys.argv)
    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    setup_requirements = ['setuptools_scm']
    if needs_sphinx:
        setup_requirements.append('sphinx>=1.3')
    if needs_pytest:
        setup_requirements.append('pytest-runner')
    install_requirements = ['requests[security]', 'six']
    test_requirements = [
        'httpretty',
        'mock',
        'pytest>=2.8.0',
        'pytest-cov',
        'pytest-httpretty',
    ]
    # Readthedocs requires Sphinx extensions to be specified as part of
    # install_requires in order to build properly.
    on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
    if on_rtd:
        install_requirements.extend(setup_requirements)
    if sys.version_info < (3,):
        install_requirements.append('backports.csv')
    with io.open('README.rst') as fp:
        readme = fp.read()
    setuptools.setup(
        name='matchlightsdk',
        license='BSD',
        description=('Software development kit for the Terbium Labs '
                     'Matchlight product.'),
        long_description=readme + '\n',
        author='Terbium Labs',
        author_email='developers@terbiumlabs.com',
        url='https://terbiumlabs.com',
        packages=setuptools.find_packages('src'),
        package_dir={'': 'src'},
        use_scm_version=True,
        package_data={
            '': ['LICENSE', 'LICENSES'],
            'pylibfp': [
                'lib/*.so',
                'lib/*.dll',
                'lib/*.dylib',
            ],
        },
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Financial and Insurance Industry',
            'Intended Audience :: Healthcare Industry',
            'Intended Audience :: Information Technology',
            'Intended Audience :: Legal Industry',
            'Intended Audience :: Science/Research',
            'Natural Language :: English',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        install_requires=install_requirements,
        setup_requires=setup_requirements,
        tests_require=test_requirements,
    )


if __name__ == '__main__':
    setup()
