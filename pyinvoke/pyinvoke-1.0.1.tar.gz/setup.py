
import os
import sys
from setuptools import setup

def readme():
  if os.path.isfile('README.md') and any('dist' in x for x in sys.argv[1:]):
    if os.system('pandoc -s README.md -o README.rst') != 0:
      print('-----------------------------------------------------------------')
      print('WARNING: README.rst could not be generated, pandoc command failed')
      print('-----------------------------------------------------------------')
      if sys.stdout.isatty():
        input("Enter to continue... ")
    else:
      print("Generated README.rst with Pandoc")

  if os.path.isfile('README.rst'):
    with open('README.rst') as fp:
      return fp.read()
  return ''

setup(
  name='pyinvoke',
  version='1.0.1',
  license='MIT',
  long_description=readme(),
  url='https://github.com/NiklasRosenstein/py-invoke',
  author='Niklas Rosenstein',
  author_email='rosensteinniklas@gmail.com',
  py_modules=['pyinvoke']
)
