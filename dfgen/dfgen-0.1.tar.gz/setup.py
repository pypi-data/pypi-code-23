# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='dfgen',
    version='0.1',
    description='  A little tool to generate commonly used ci/cd templates like Dockerfiles.',
    author='Merlijn Tishauser',
    author_email='merlijn@gargleblaster.org',
    url='https://github.com/merlijntishauser/dfgen',
    download_url='https://github.com/merlijntishauser/dfgen/archive/v0.1.tar.gz',
    keywords=['templates', 'docker', 'Dockerfile'],
    classifiers=[],
    packages=[
        'dfgen',
        'dfgen.templates',
        'dfgen.templates.docker',
        'dfgen.scripts'
    ],
    package_data={
        'dfgen.templates': ['*.jinja2'],
        'dfgen.templates.docker': ['*.jinja2'],
        'dfgen.scripts': ['*.sh']
    },
    scripts=['bin/dfgen'],
    install_requires=[
        "certifi",
        "click",
        "click-log",
        "chardet",
        "Jinja2",
        "idna",
        "MarkupSafe",
        "pip",
        "requests",
        "setuptools",
        "urllib3",
        "wheel"
    ],
    extras_require={
        'test': [
            "mock",
            "pytest",
            "pytest-mock",
            "pytest-cov",
            "tzlocal"
        ]
    },
    zip_safe=False
)
