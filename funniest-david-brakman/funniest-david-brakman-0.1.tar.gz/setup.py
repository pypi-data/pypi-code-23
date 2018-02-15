# Following example at http://python-packaging.readthedocs.io/en/latest/minimal.html
from setuptools import setup

setup(name='funniest-david-brakman',
      version='0.1',
      description='The funniest joke in the world',
      url='http://github.com/storborg/funniest',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['funniest-david-brakman'],
      zip_safe=False)
