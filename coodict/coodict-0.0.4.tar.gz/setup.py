import sys
from setuptools import setup, find_packages
sys.path.append("coodict")
from version import get_version

requires = []

setup(
  name = 'coodict',
  packages = find_packages(),
  install_requires=requires,
  version=get_version(),
  description = 'A (Scottish) copy-on-write dictionary wrapper class.',
  author = 'Matthew Richardson',
  author_email = 'm.richardson@ed.ac.uk',
  license = 'GNU Affero General Public License v3 or later (AGPLv3+)',
  url = 'https://github.com/mrichar1/coodict',
  keywords = ['python', 'dictionary', 'copy-on-write', 'cow'],
  classifiers = [
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
      'Topic :: Software Development :: Libraries :: Python Modules',
  ],
  test_suite="tests",
  )
