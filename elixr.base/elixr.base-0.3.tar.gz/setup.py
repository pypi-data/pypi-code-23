import os
from setuptools import setup, find_packages


## meta data
__author__  = 'Hazeltek Solutions'
__version__ = '0.3'


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()


requires = []
tests_requires = [
    'pytest',
    'pytest-cov'
]

setup(
    name='elixr.base',
    version=__version__,
    description='A python general purpose utility library',
    long_description=README + '\n\n' + CHANGES,
    author=__author__,
    author_email='info@hazeltek.com',
    maintainer='Abdul-Hakeem Shaibu',
    maintainer_email='hkmshb@gmail.com',
    url='https://github.com/babdulhakim2/elixr.base.git',
    keywords='elixr.base, hazeltek elixr.base',
    zip_safe=False,
    packages=find_packages(),
    platforms='any',
    install_requires=requires,
    extras_require={ 'testing': tests_requires },
    classifiers=[]
)