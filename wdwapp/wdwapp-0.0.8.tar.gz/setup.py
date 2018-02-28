import os

from setuptools import setup, find_packages

from wdwapp import __version__

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'deform',
    'sqlalchemy',
    'pyramid_tm',
    'gunicorn',
    'zope.sqlalchemy',
    'mysqlclient',
    'meteocalc',
    'requests',
    'bcrypt',
]

setup(name = 'wdwapp',
    version = __version__,
    description = 'Webapps for recording and displaying weather data',
    long_description = README + '\n\n' + CHANGES,
    author = 'Frédéric KIEBER',
    author_email = 'contact@frkb.fr',
    license = 'MIT',
    url = '',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Framework :: Pyramid',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
    ],
    keywords = 'webapp wdwsrv weather',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = requires,
    entry_points = {
        'paste.app_factory': [
            'main = wdwapp:main',   # main from __init__.py
        ],
        'console_scripts' : [
            'wdwapp_initialize_db = wdwapp.initialize_db:main',
            'wdwapp_cron = wdwapp.cron:main',
        ],
    },
)

