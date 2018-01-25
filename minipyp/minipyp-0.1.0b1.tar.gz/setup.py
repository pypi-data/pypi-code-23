from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as file:
    readme = file.read()
there = {}
with open(path.join(here, 'minipyp', 'minipyp.py'), encoding='utf-8') as file:
    exec(file.read(), there)
    if '__version__' not in there.keys():
        raise Exception('Failed to fetch version from source')
setup(
    name='minipyp',
    version=there['__version__'],
    description='A more traditional web server',
    long_description=readme,
    url='https://github.com/RyanGarber/minipyp',
    author='Ryan Garber',
    author_email='ryanmichaelgarber@gmail.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Natural Language :: English',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='http https web cgi fast-cgi fpm ssl tls socket proxy reverse',
    packages=find_packages(exclude=['docs', 'tests']),
    download_url='https://github.com/RyanGarber/minipyp/archive/0.1.0b1.tar.gz',
    install_requires=['requests', 'h2'],
    extras_require={'tests': ['unittest']},
    python_requires='>=3'
)
