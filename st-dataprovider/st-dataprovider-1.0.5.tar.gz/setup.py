# Copyright 2017 Shortest Track Company. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

# To publish to PyPi use: python setup.py bdist_wheel upload -r pypi

from setuptools import setup

version = '1.0.5'

setup(
  name='st-dataprovider',
  version=version,
  namespace_packages=['st_library'],
  packages=[
    'st_library.dataprovider',
    'st_library.dataprovider.structured_data',
    'st_library.dataprovider.unstructured_data'
  ],
  description='shortest track dataprovider',
  author='Fugui Xing',
  author_email='admin@shortesttrack.com',
  url='https://github.com/shortesttrack/dataprovider-py',
  download_url='https://github.com/shortesttrack/dataprovider-py/archive/v1.0.5.zip',
  keywords=[
    'Shortest Track',
    'st_library',
    'dataprovider'
  ],
  license="Apache Software License",
  classifiers=[
      "Programming Language :: Python",
      "Programming Language :: Python :: 2",
      "Programming Language :: Python :: 3",
      "Environment :: Other Environment",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: Apache Software License",
      "Operating System :: OS Independent",
      "Topic :: Software Development :: Libraries :: Python Modules"
  ],
  long_description="""\
Support package for Shortest Track Library. This provides Python APIs
for accessing Shortest Track Platform services such as structured data storage.
  """,
  install_requires=[
    'httplib2==0.10.3',
    'oauth2client==2.2.0',
    'future==0.16.0',
    'pandas==0.19.1',
    'pandas-profiling>=1.0.0a2',
    'python-dateutil==2.5.0',
    'pytz>=2015.4',
    'pyyaml==3.11',
    'requests==2.9.1',
    'ipykernel==4.5.2',
    'psutil==4.3.0',
    'jsonschema==2.6.0',
    'six==1.10.0',
    'urllib3==1.22',
  ]
)
