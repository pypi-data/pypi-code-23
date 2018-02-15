from setuptools import setup

setup(
  name='iscraper',
  version='0.3',
  description='Front end for get-iplayer to allow download by name.',
  url='https://github.com/oldironhorse/iscraper',
  download_url='https://github.com/oldironhorse/iscraper/archive/0.3.tar.gz',
  author='Simon Redding',
  author_email='s1m0n.r3dd1ng@gmail.com',
  license='GPL 3.0',
  packages=['iscraper'],
  install_requires=[
    'bs4',
  ],
  test_suite='nose.collector',
  tests_require=['nose'],
  zip_safe=False)
