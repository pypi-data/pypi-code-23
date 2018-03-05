"""
Flask-ClickHouse
-------------
ClickHouse support for Flask applications.

Installation
============
Flask-ClickHouse is pip-installable:
    pip install -U ClickHouse

Development
===========
Source code is hosted in `GitHub <https://github.com/aolefira/flask-clickhouse>`_
(contributions are welcome!)
"""

from setuptools import setup, find_packages

requires = [
    'clickhouse-driver>=0.0.9',
]

setup(
    name='Flask-ClickHouse',
    description='ClickHouse support for Flask applications',
    version='1.0.0',
    url='https://github.com/aolefira/flask-clickhouse',
    license='GNU General Public License v3.0',
    author='Andrew Olefira',
    author_email='andrew.olefira@gmail.com',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
