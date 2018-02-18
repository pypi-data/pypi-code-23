"""raynbow, a spectral data analysis module."""
from setuptools import setup

setup(
    name='raynbow',
    version='0.0.1',
    description='A python module for analysis of spectral data',
    long_description='',
    license='MIT',
    author='Brandon Dube',
    author_email='brandondube@gmail.com',
    url='https://github.com/brandondube/raynbow',
    packages=['raynbow'],
    install_requires=['numpy', 'scipy', 'matplotlib'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ]
)
