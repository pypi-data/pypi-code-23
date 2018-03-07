""" See [1] on how to write proper `setup.py` script.

[1] https://github.com/pypa/sampleproject/blob/master/setup.py
"""


from setuptools import find_packages, setup
from as_dataframe import __version__


setup(
    name='as_dataframe',
    version=__version__,
    description='Convert nested dictionaries into dataframes.',
    author='Dmitrii Izgurskii',
    author_email='izgurskii@gmail.com',
    license='MIT',
    url='http://test.org',
    packages=find_packages(exclude=['contrib', 'docs', '*test*'])
)

