#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Google Cloud Dataflow SDK for Python setup file."""

import setuptools


PACKAGE_NAME = 'google-cloud-dataflow'
PACKAGE_VERSION = '2.3.0'
PACKAGE_DESCRIPTION = (
    'Google Cloud Dataflow SDK for Python, based on Apache Beam')
PACKAGE_URL = 'https://cloud.google.com/dataflow/'
PACKAGE_DOWNLOAD_URL = 'https://pypi.python.org/pypi/google-cloud-dataflow'
PACKAGE_AUTHOR = 'Google, Inc.'
PACKAGE_EMAIL = 'dataflow-sdk@google.com'
PACKAGE_KEYWORDS = 'google cloud dataflow apache beam'
PACKAGE_LONG_DESCRIPTION = '''
Apache Beam is an open-source, unified programming model for
describing large-scale data processing pipelines. This redistribution of
Apache Beam is targeted for executing batch Python pipelines on
Google Cloud Dataflow.
'''

REQUIRED_PACKAGES = [
    'apache-beam[gcp]==' + PACKAGE_VERSION,
]


setuptools.setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description=PACKAGE_DESCRIPTION,
    long_description=PACKAGE_LONG_DESCRIPTION,
    url=PACKAGE_URL,
    download_url=PACKAGE_DOWNLOAD_URL,
    author=PACKAGE_AUTHOR,
    author_email=PACKAGE_EMAIL,
    packages=setuptools.find_packages(),
    install_requires=REQUIRED_PACKAGES,
    test_suite='nose.collector',
    zip_safe=False,
    # PyPI package information.
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    license='Apache License, Version 2.0',
    keywords=PACKAGE_KEYWORDS,
)
