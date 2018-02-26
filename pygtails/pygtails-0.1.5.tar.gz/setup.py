from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='pygtails',
      version='0.1.5',
      description='A simple wrapper around pygame',
      long_description=long_description,
      url='http://pygtails.readthedocs.io/en/latest/',
      author='Josie Thompson',
      classifiers=['Development Status :: 1 - Planning',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Software Development :: Libraries :: pygame'],
      python_requires=">=3",
      package_dir={'': 'src'},
      packages=[''],
      project_urls={'Source': 'https://github.com/josiest/pygtails/'})
