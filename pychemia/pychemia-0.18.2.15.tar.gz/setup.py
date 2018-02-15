import os
from setuptools import setup, find_packages

###################################################################

NAME = "pychemia"
PACKAGES = find_packages()
META_PATH = os.path.join("src", "attr", "__init__.py")
KEYWORDS = ["electronic", "structure", "analysis", "materials", "discovery", "metaheuristics"]
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
INSTALL_REQUIRES = ['numpy >= 1.12.0',
                    'scipy >= 0.18.0',
                    'future>=0.16.0',
                    'spglib>=1.9.9',
                    'pymongo>=3.4.0']

###################################################################

setup(
    name=NAME,
    version='0.18.2.15',
    author='Guillermo Avendano-Franco',
    author_email='gufranco@mail.wvu.edu',
    packages=find_packages(),
    url='https://github.com/MaterialsDiscovery/PyChemia',
    license='LICENSE.txt',
    description='Python framework for Materials Discovery and Design',
    long_description=open('README').read(),
    install_requires=INSTALL_REQUIRES,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
)
