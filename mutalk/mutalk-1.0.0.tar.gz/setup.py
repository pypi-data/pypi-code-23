from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mutalk',
    version='1.0.0',
    description='Mutlicast messaging library',
    long_description=long_description,
    url='https://github.com/mutalk/python',
    author='Baryshnikov Alexander',
    author_email='dev@baryshnikov.net',
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='mutalk multicast messaging',
    install_requires=[],
    entry_points={

    }
)