# coding: utf-8
# __author = 'elkan1788@gmail.com'

from setuptools import setup, find_packages
from pip.req import parse_requirements

INSTALL_REQ = parse_requirements('requirements.txt', session='hack')
REQUIRES = [str(ir.req) for ir in INSTALL_REQ]

"""
Email Job setup requires 
"""
setup(
    name='hive-email-job',
    version='2.1.1',
    description='Use Python implements get data from Hive then send attachments to user.',
    author='elkan1788',
    author_email='elkan1788@gmail.com',
    license='Apache License V2.0',
    install_requires=REQUIRES,
    packages=find_packages(),
    long_description=open("README.rst").read(),
    url='https://github.com/elkan1788/HiveEmailJob',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ]
)
