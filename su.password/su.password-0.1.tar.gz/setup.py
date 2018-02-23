from setuptools import setup, find_packages
from codecs import open
from os import path

VERSION = "0.1"
NAME = "password"
DESCRIPTION = "A simple password management lib."
INSTALL_REQUIRES = [
    'setuptools',
    'su.aes'
]

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="su." + NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    url='https://github.com/zhaolins/su.' + NAME,
    author='Zhaolin Su',
    author_email='z@suho.me',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='development',
    namespace_packages=['su'],
    include_package_data=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=INSTALL_REQUIRES
)
