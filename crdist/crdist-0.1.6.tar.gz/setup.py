'''
Created on 16/12/2015

@author: luisza
'''

from setuptools import setup, find_packages
import os

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
]

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# Dynamically calculate the version based on django.VERSION.
version = __import__('crdist').get_version()

setup(
    author='Luis Zarate Montero',
    author_email='luis.zarate@solvosoft.com',
    name='crdist',
    version=version,
    description='Costa Rican Geografic distribution for model admin in Django.',
    long_description=README,
    url='https://github.com/solvo/crdist',
    license='GNU General Public License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'setuptools',
        'django>=1.8',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
)
