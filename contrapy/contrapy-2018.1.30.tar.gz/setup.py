import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme_rst = f.read()

setup(
    name='contrapy',
    url='https://github.com/digitalmensch/contrapy',
    download_url='https://pypi.python.org/pypi/contrapy',
    description='Contracts for Python',
    long_description=readme_rst,
    keywords='contracts, contracts-programming',
    platforms='any',
    license="MIT",
    version='2018.01.30',
    author='Tobias Ammann',
    py_modules=['contrapy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
