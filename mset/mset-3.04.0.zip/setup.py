
from setuptools import find_packages, setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

try:
    with open(path.join(here, 'readme.rst'), encoding='utf-8') as f:
        long_description = f.read()
except(IOError, ImportError):
    long_description = ""

setup(
    name='mset',
    author='Marmoset LLC',
    author_email='support@marmoset.co',
		version="3.04.0",
    license='MIT',
    keywords=['mset', 'marmoset', 'toolbag', 'hexels'],
    download_url='https://marmoset.co/toolbag/',
    description='A no-op version of the runtime python library included in Marmoset Toolbag.',
    long_description=long_description,
    url='https://marmoset.co',
    classifiers=[
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'License :: Public License (LGPL) :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    platforms='ANY',
    packages=find_packages(exclude=['tests*']),
    data_files=['readme.rst'],
    include_package_data=True,
)

