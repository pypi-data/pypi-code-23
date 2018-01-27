# -*- coding: utf-8 -*-
import setuptools
import os
from numpy import distutils
import distutils.command.install_data

#this is to get the __version__ from version.py
with open('jscatter/version.py','r') as f:  exec(f.read())

with open('README.rst') as readme_file:
    long_description = readme_file.read()

EXTENSIONS=[]
#EXTENSIONS.append(distutils.core.Extension( 'contin-linux', ['contin.f']) )

distutils.core.setup(name='jscatter',
      version=__version__,
      description='Combines dataArrays with attributes for fitting, plotting and analysis including models for Xray and neutron scattering',
      long_description=long_description,
      author='Ralf Biehl',
      author_email='ra.biehl@fz-juelich.de',
      url='https://gitlab.com/biehl/jscatter',
      platforms=["osx","linux"],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: Physics',
          ],
      include_package_data=True,
      py_modules=[],
      packages=setuptools.find_packages(exclude=['build']),
      package_data = { '': ['*.txt', '*.rst','*.dat','*.html']   },
      #data_files = datafiles,
      #cmdclass = {  },
      dependency_links=[''],
      install_requires=["numpy >= 1.8 ",
                        "scipy >= 0.13"],
      ext_modules = EXTENSIONS,
      test_suite='jscatter.test_all'
     )
      



