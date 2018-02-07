import os
from setuptools import setup, find_packages

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = ['pysha3']
setup(
    name = "ph4_moneropy",
    version = "0.0.3",
    description = "A python toolbox for Monero.",
    long_description=read('README.md'),
    url = "https://github.com/monero-monitor/moneropy",
    keywords = "monero",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
    ],
    license = "BSD-3-Clause"
)
