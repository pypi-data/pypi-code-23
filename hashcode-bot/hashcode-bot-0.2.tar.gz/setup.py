#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='hashcode-bot',
    version='0.2',
    description='Utilities to rule Google HashCodes',
    author='Jonathan Stoppani',
    author_email='jonathan@stoppani.name',
    url='https://github.com/GaretJax/hashcode-bot',
    license='MIT',
    install_requires=[
        'attrs',
        'pendulum',
        'requests',
        'click',
        'halo',
        'pyyaml',
        'keyring',
        'keyrings.alt',
        'google_auth_oauthlib',
        'google-api-python-client',
        'google-auth',
        'google-auth-httplib2',
    ],
    entry_points={
        'console_scripts': [
            'hc=hclib.__main__:main',
        ],
    },
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
