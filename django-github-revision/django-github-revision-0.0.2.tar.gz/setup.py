import sys
from os import path
from os import system

from setuptools import setup

here = path.abspath(path.dirname(__file__))

install_deps = [
    'dealer',
    'django'
]

tests_deps = [
    'mock'
]

extras = {
    'tests': tests_deps,
}

version = '0.0.2'

# Get the long description from the README file
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

if sys.argv[-1] == 'publish':
    try:
        import wheel
    except ImportError:
        raise ImportError("Fix: pip install wheel")
    system('python setup.py sdist bdist_wheel --universal upload')
    sys.exit()

setup(
    name='django-github-revision',
    version=version,
    packages=['github_revision', 'github_revision.templatetags'],
    url='https://github.com/watchdogpolska/django-github-revision',
    license='MIT',
    author='Adam Dobrawy',
    author_email='karol.bregula@siecobywatelska.pl',
    description='Publishes information about the git revision that is running and links to the GitHub repository.',
    install_requires=install_deps,
    tests_require=tests_deps,
    extras_require=extras
)
