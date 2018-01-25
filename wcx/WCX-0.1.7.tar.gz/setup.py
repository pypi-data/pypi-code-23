
# Always prefer setuptools over distutils
from setuptools import setup

import os

long_description = 'WCX wallets are most secured digital wallets which are used to send and receive virtual currencies like bitcoin.'
if os.path.exists('README.txt'):
    long_description = open('README.txt').read()

setup(
      name='WCX',
      version='0.1.7',
      description='The easiest way to integrate WCX Api Functions in your applications. Sign up at WCX.com for your API key.',
      long_description=long_description,
      author='OsizTech',
      author_email='veerasarma@osiztechnologies.com',
      license='ISC',
      url = "http://www.osiztechnologies.com/",
      keywords = "WCX wcx_wallet bitcoin_api wcx wallet wcx_wallet_api",
      packages=['wcx'],
      install_requires=[
          'requests',
          'pycrypto',
          'ecdsa',
          'six',
          'base58'
      ],
      zip_safe=False
      )

# for packages not on pypi
# dependency_links=['http://github.com/user/repo/tarball/master#egg=package-1.0']
