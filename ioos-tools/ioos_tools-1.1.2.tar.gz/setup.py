from __future__ import absolute_import, division, print_function

import os
import sys
import versioneer
from setuptools import find_packages, setup

rootpath = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return open(os.path.join(rootpath, *parts), 'r').read()


email = "ocefpaf@gmail.com"
maintainer = "Filipe Fernandes"
authors = ['Rich Signell', 'Filipe Fernandes']

LICENSE = read('LICENSE.txt')
long_description = '{}\n{}'.format(read('README.rst'), read('CHANGES.txt'))


with open('requirements.txt') as f:
    tests_require = f.readlines()
install_requires = [t.strip() for t in tests_require]


setup(name='ioos_tools',
      version=versioneer.get_version(),
      packages=find_packages(),
      cmdclass=versioneer.get_cmdclass(),
      license=LICENSE,
      long_description=long_description,
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Education',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Education',
                   'Topic :: Scientific/Engineering'],
      description='Misc functions for IOOS notebooks',
      author=authors,
      author_email=email,
      maintainer='Filipe Fernandes',
      maintainer_email=email,
      url='https://github.com/pyoceans/ioos_tools/releases',
      platforms='any',
      keywords=['oceanography', 'data analysis'],
      install_requires=install_requires,
      zip_safe=False,
      )
