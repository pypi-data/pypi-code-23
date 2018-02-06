"""About datarobot
=========================
.. image:: https://img.shields.io/pypi/v/datarobot.svg
   :target: https://pypi.python.org/pypi/datarobot/
.. image:: https://img.shields.io/pypi/pyversions/datarobot.svg
.. image:: https://img.shields.io/pypi/status/datarobot.svg

DataRobot is a client library for working with the `DataRobot`_ platform API.

Installation
=========================
Python 2.7 and >= 3.4 are supported.
You must have a datarobot account.

::

   $ pip install datarobot

Usage
=========================
The library will look for a config file `~/.config/datarobot/drconfig.yaml` by default.
This is an example of what that config file should look like.

::

   token: your_token
   endpoint: https://app.datarobot.com/api/v2

Alternatively a global client can be set in the code.

::

   import datarobot as dr
   dr.Client(token='your_token', endpoint='https://app.datarobot.com/api/v2')

Alternatively environment variables can be used.

::

   export DATAROBOT_API_TOKEN='your_token'
   export DATAROBOT_ENDPOINT='https://app.datarobot.com/api/v2'

See `documentation`_ for example usage after configuring.

Tests
=========================
::

   $ py.test

.. _datarobot: http://datarobot.com
.. _documentation: https://datarobot-public-api-client.readthedocs-hosted.com
"""

import re
from setuptools import setup

with open('datarobot/_version.py') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

tests_require = ['mock', 'pytest-cov', 'responses']

dev_require = tests_require + [
    'flake8',
    'green',
    'ipython>=4.1,<5',
    'sphinx',
    'nbsphinx>=0.2.9,<1',
    'nbconvert>=5.3,<6',
    'numpydoc>=0.6.0',
    'tox',
]

example_require = [
    'ipython<=5.0',  # python2.7 compatablilty
    'jupyter<=5.0',
    'fredapi==0.4.0',
    'matplotlib<=2.0.2',
    'seaborn<=0.8',
    'sklearn<=0.18.2',
    'wordcloud<=1.3.1',
    'colour<=0.1.4'
]

setup(
    name='datarobot',
    version=version,
    description='This client library is designed to support the DataRobot API.',
    author='datarobot',
    author_email='support@datarobot.com',
    maintainer='datarobot',
    maintainer_email='info@datarobot.com',
    url='http://datarobot.com',
    license='Apache Software License',
    packages=[
        'datarobot',
        'datarobot.models',
        'datarobot.utils',
        'datarobot.helpers',
        'datarobot.ext',
    ],
    long_description=__doc__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'pandas>=0.15',
        'pyyaml>=3.11',
        'requests_toolbelt>=0.6',
        'trafaret>=0.7,<1.1',
    ],
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    extras_require={
        'dev': dev_require,
        'examples': example_require
    }
)
