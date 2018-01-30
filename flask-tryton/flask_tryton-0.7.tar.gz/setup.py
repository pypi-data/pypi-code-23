# This file is part of flask_tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import os
import io
from setuptools import setup


def read(fname):
    return io.open(
        os.path.join(os.path.dirname(__file__), fname),
        'r', encoding='utf-8').read()

setup(name='flask_tryton',
    version='0.7',
    author='B2CK',
    author_email='info@b2ck.com',
    url='http://flask-tryton.b2ck.com/',
    description='Adds Tryton support to Flask application',
    long_description=read('README'),
    py_modules=['flask_tryton'],
    zip_safe=False,
    platforms='any',
    keywords='flask tryton web',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Tryton',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    license='GPL-3',
    install_requires=[
        'Flask>=0.8',
        'Werkzeug',
        'trytond>=3.0',
        ],
    use_2to3=True,
    )
