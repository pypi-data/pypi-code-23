from setuptools import setup
from setuptools import find_packages

setup(
    name='BlastRadius',
    version='0.1.8',
    author='Patrick McMurchie',
    author_email='patrick.mcmurchie@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/blast-radius'],
    url='http://pypi.python.org/pypi/BlastRadius/',
    license='LICENSE.txt',
    description='Interactive visualizations of Terraform dependency graphs',
    long_description=open('README.md').read(),
    install_requires=[
        "Flask",
        "jinja2",
        "pyhcl",
        "requests",
        "BeautifulSoup4"
    ],
)
