from setuptools import setup

setup(
  name='awsclientbot',
  version='0.1.0',
  description='Client for AWS Client Bot',
  author='Ivan Tertychnyy',
  author_email='itertychnyy@gmail.com',
  packages=['awsclientbot'],
  url='https://github.com/tertychnyy/awsclientbot',
  license='LICENSE.txt',
  install_requires=[
        "requests>=2.10.0",
    ],
  project_urls={
    'Documentation': 'http://awsclientbot.readthedocs.io/en/latest/',
    'Tracker': 'https://github.com/tertychnyy/awsclientbot/issues',
  },
)
