#!/usr/bin/env python3

from setuptools import setup, find_packages

import quantum_dynamics as my_pkg

setup(name='quantum_dynamics',
      author=my_pkg.__author__,
      author_email=my_pkg.__author_email__,
      classifiers=[
          'License :: OSI Approved :: Boost Software License 1.0 (BSL-1.0)',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Scientific/Engineering :: Physics'
      ],
      description='Quantum mechanics in 1D.',
      install_requires=['numpy', 'scipy', 'matplotlib', 'h5py', 'progressbar2'],
      keywords='numerics linear algebra schrödinger quantum',
      license=my_pkg.__license__,
      long_description=open("README.rst","r").read(),
      packages=find_packages(),
      python_requires='>=3.5',
      scripts=['scripts/qdyn_laser',
               'scripts/plot_time_evolution'],
      test_suite='nose2.collector.collector',
      tests_require=['nose2'],
      url='https://compphys.solanpaa.fi',
      version=my_pkg.__version__,
      zip_safe=True)
