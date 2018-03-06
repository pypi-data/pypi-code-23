#!/usr/bin/env python

from io import open

from setuptools import find_packages, setup

setup(
    name='django-images-placeholder',
    version='0.0.1',
    description='Automatic generates images with the right dimensions when'
                'it\'s missing from the local media storage based on a common'
                'database or remote MEDIA_URL.',
    long_description=open('README.md', encoding='utf-8').read(),
    author='Joao Vitor Gomes [at] The Goodfellas',
    author_email='joao.gomes@thegoodfellas.com.br',
    url='https://bitbucket.org/3mwdigital/django-images-placeholder',
    # download_url='https://pypi.python.org/pypi/django-images-placeholder',
    license='BSD 2',
    packages=find_packages(exclude=('tests.*', 'tests', 'example')),
    install_requires=[
        # 'Django>=1.9.7',
    ],
    include_package_data=True,
    #zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
