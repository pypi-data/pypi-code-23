from setuptools import setup

setup(name='simpletools',
      version='0.1.3',
      description='simpletools',
      url='https://github.com/getsimpletools/simpletools-python/tree/master',
      author='Marcin Rosinski',
      author_email='marcin@getsimpletools.com',
      license='BSD-3',
      packages=['simpletools'],
      install_requires=['pika'],
      zip_safe=False)