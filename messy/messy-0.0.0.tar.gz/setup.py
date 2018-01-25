from setuptools import (setup,
                        find_packages)

import messy
from messy.config import PROJECT_NAME

project_base_url = 'https://github.com/not4drugs/messy/'

setup_requires = [
    'pytest-runner>=3.0'
]
tests_require = [
    'pydevd>=1.1.1',  # debugging
    'pytest>=3.3.0',
    'pytest-cov>=2.5.1',
    'hypothesis>=3.38.5',
]

setup(name=PROJECT_NAME,
      packages=find_packages(exclude=('tests',)),
      version=messy.__version__,
      description=messy.__doc__,
      long_description=open('README.md').read(),
      author='John Doe',
      author_email='not4drugs@protonmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      setup_requires=setup_requires,
      tests_require=tests_require)
