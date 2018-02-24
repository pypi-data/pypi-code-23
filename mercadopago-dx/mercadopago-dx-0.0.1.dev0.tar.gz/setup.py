#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import re
from setuptools import setup

with io.open('docs/README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('sdk/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='mercadopago-dx',
    version=version,
    url='https://github.com/mercadopago/dx-python',
    license='MIT',
    author='Lucas Emmanuel Bais',
    author_email='lucas.bais@mercadopago.com',
    maintainer='Lucas Emmanuel Bais',
    maintainer_email='developers@mercadolibre.com',
    description='Devtools for MercadoPago services',
    long_description=readme,
    keywords='mercadopago sdk development',
    packages=['sdk'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'certifi>=2018.1.18',
        'chardet>=3.0.4',
        'idna>=2.6',
        'requests>=2.18.4',
        'urllib3>=1.22'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
