from distutils.core import setup
import os
from setuptools import setup, find_packages

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
  name = 'elask',
  packages=find_packages(),
  include_package_data=True,
  scripts=['elask/bin/elask-admin.py'],
  entry_points={'console_scripts': [
      'elask-admin = elask.core.management:execute_from_command_line',
  ]},
  install_requires=[
    'elasticsearch-dsl==6.0.1',
    'flasgger==0.8.0',
    'Flask==0.12.2',
    'Flask-JWT==0.3.2',
    'Flask-RESTful==0.3.6',
    'marshmallow==2.15.0',
    'zappa==0.45.1',
    'bcrypt==3.1.4'],
  version = '2.1',
  description = 'elask rest framework',
  author = 'Partha Saradhi',
  author_email = 'parthasaradhi1992@gmail.com',
  url = '', # use the URL to the github repo
  download_url = '', # I'll explain this in a second
  keywords = ['elasticsearch', 'rest', 'rest api'], # arbitrary keywords
  classifiers = [],
)
