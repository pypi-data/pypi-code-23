from os import path
from distutils.core import setup
from codecs import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='JsonLogFormatter',
    version='1.0.1',
    packages=['json_formatter', ],
    description='Json log formatter',
    long_description=long_description,
    author='Team Chili Zooplus AG',
    author_email='team_dev_chili@zooplus.com',
    extras_require={
        'test': ['pytest'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Logging',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    project_urls={
        'Source': 'https://github.com/ObadaAlexandru/JsonLogFormatter',
    }
)
