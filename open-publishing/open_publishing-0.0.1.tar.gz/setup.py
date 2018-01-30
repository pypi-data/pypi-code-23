"""Module for setting up open publishing library python object."""

from setuptools import setup, find_packages

REQUIRES = [
    'PyYAML',
    'jsonschema'
]

VERSION = '0.0.1'

setup(
    name='open_publishing',
    description='API Wrapper for Open Publishing API',

    version=VERSION,
    download_url='https://github.com/open-publishing/open-publishing-api/archive/'+VERSION+'.zip',
    url='https://api.openpublishing.com/',

    author='Open Publishing GmbH',
    author_email='info@openpublishing.com',
    license='Open Publishing License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
        ],
    packages=find_packages(),
    install_requires=REQUIRES,
    keywords='publishing book ebook',
    zip_safe=False)
