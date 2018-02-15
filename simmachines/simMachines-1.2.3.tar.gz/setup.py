from setuptools import setup, find_packages

version = '1.2.3'

setup(name='simMachines',
      packages = find_packages(exclude=['example*']),
      install_requires=['requests','numpy','pandas'],
      version=version,
      description="A library to use simMachines, Inc. API",
      python_requires='>=3',
      author = 'Rick Palmer',
      author_email = 'rickpalmer@simmachines.com'
      )