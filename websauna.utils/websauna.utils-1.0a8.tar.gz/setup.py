# Standard Library
import sys
from codecs import open
from os import path

from setuptools import find_packages
from setuptools import setup


assert sys.version_info >= (3, 5, 2), "websauna.utils needs Python 3.5.2 or newer, you have {version}".format(version=sys.version_info)

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='websauna.utils',
    namespace_packages=["websauna"],
    version='1.0a8',
    description=long_description.split("\n")[0],
    long_description=long_description,
    url='https://websauna.org',
    author='Mikko Ohtamaa',
    author_email='mikko@opensourcehacker.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    keywords='config pytest websauna',
    packages=find_packages(exclude=['docs']),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.5.2',
    install_requires=[

        # User management
        "authomatic",

        # Console logging
        "rainbow_logging_handler",
    ],

    extras_require={
        # Dependencies needed to build and release Websauna
        'dev': [
            'pyroma==2.2',  # This is needed until version 2.4 of Pyroma is released
            'sphinx>=1.6.1',
            'sphinx-autodoc-typehints',
            'sphinx_rtd_theme',
            'sphinxcontrib-zopeext',
            'zest.releaser[recommended]'
        ],
        'test': [
            'codecov',
            'flake8',
            'pytest>=3.0',
            'pytest-runner',
            'coverage',
            'flaky',
            'isort',
            'pytest-cov',
            'pytest-runner',
            'pytest-timeout',
        ],
        "notebook": [
            "ipython[notebook]<5.2",
        ],
        "sqlalchemy": [
            # This package just uses sqlalchemy to enable websauna.utils.jsonb.is_index_property
            "sqlalchemy",
        ]
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'plaster.loader_factory': [
           'ws=websauna.utils.config.loader:Loader',
        ],
        'plaster.wsgi_loader_factory': [
            'ws=websauna.utils.config.loader:Loader',
        ],
    },
)
