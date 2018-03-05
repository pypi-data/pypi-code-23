from setuptools import setup, find_packages
from siapatools.__init__ import __version__


setup(
    name="siapatools",
    version=__version__,
    author="Rafael Alves Ribeiro",
    author_email="rafael.alves.ribeiro@gmail.com",
    packages=["siapatools"],
    install_requires=[
        "pandas",
        "psycopg2",
    ],
)
