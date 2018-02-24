# coding=utf-8
"""
Etcher's stupid library
"""

import os

from pip.req import parse_requirements
from setuptools import find_packages, setup

requirements = [str(r.req) for r in
                parse_requirements('requirements.txt', session=False)]
test_requirements = [str(r.req) for r in
                     parse_requirements('requirements-dev.txt', session=False)]

CLASSIFIERS = filter(None, map(str.strip,
                               """
Development Status :: 3 - Alpha
Environment :: Win32 (MS Windows)
Intended Audience :: Developers
Natural Language :: English
Operating System :: Microsoft :: Windows :: Windows 7
Operating System :: Microsoft :: Windows :: Windows 8
Operating System :: Microsoft :: Windows :: Windows 8.1
Operating System :: Microsoft :: Windows :: Windows 10
License :: OSI Approved :: MIT License
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Topic :: Utilities
""".splitlines()))


def read_local_files(*file_paths: str) -> str:
    """
    Reads one or more text files and returns them joined together.

    A title is automatically created based on the file name.

    :param file_paths: list of files to aggregate

    """

    def _read_single_file(file_path):
        with open(file_path) as f:
            filename = os.path.splitext(file_path)[0]
            title = f'{filename}\n{"=" * len(filename)}'
            return '\n\n'.join((title, f.read()))

    return '\n' + '\n\n'.join(map(_read_single_file, file_paths))


setup(
    name='elib',
    zip_safe=False,
    install_requires=requirements,
    tests_require=test_requirements,
    package_dir={'elib': 'elib'},
    package_data={},
    test_suite='pytest',
    packages=find_packages(),
    python_requires='>=3.6',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    license='MIT',
    classifiers=CLASSIFIERS,
)
