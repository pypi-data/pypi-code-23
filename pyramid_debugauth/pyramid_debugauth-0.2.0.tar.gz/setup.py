import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except:
    README = ''

try:
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    CHANGES = ''

requires = [
]

docs_extras = [
    'Sphinx',
    'sphinxcontrib-httpdomain'
    'livereload==1.0.1',
    ]

dev_extras = [
    'nose',
    'nose-parameterized',
    'nosexcover',
    'coverage',
    'mock',
    'webtest',
    'pyramid',

    'readme',
    'twine',
    ]

setup(
    name='pyramid_debugauth',
    version='0.2.0',
    description='Debug Authentication Policy for Pyramid',
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ],
    keywords='wsgi pylons pyramid auth authentication debug',
    author="Pior Bastida",
    author_email="pior@pbastida.net",
    url="https://github.com/pior/pyramid_debugauth",
    license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires = requires,
    extras_require = {
        'dev':dev_extras,
        'docs':docs_extras,
    },
)
