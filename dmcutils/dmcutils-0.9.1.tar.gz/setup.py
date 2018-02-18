#!/usr/bin/env python
install_requires=['python-dateutil','pytz','pandas','h5py','scikit-image','imageio',
     'histutils','morecvutils']
tests_require=['nose','coveralls']
# %%
from setuptools import setup,find_packages

setup(name='dmcutils',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/dmcutils',
      description='Utilities to read and plot DMC Experiment data',
      long_description=open('README.rst').read(),
      version='0.9.1',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
      ],
      install_requires=install_requires,
      tests_require=tests_require,
      python_requires='>=3.6',
      extras_require={'web':['flask','flask-limiter'],
                      'plot':['matplotlib'],
                      'io':['astrometry_azel'],
                      'tests':tests_require},
	  )

