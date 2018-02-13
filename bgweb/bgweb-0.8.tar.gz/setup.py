from os import path
from distutils.core import setup
from setuptools import find_packages

VERSION = "0.8"
AUTHORS = "Barcelona Biomedical Genomics Lab"
CONTACT_EMAIL = "bbglab@irbbarcelona.org"


directory = path.dirname(path.abspath(__file__))
with open(path.join(directory, 'requirements.txt')) as f:
    required = f.read().splitlines()


setup(
    name="bgweb",
    version=VERSION,
    package_data={'bgweb': ['*.conf.template', '*.confspec']},
    packages=find_packages(),
    author=AUTHORS,
    author_email=CONTACT_EMAIL,
    description="BBGLab web framework",
    url="https://bitbucket.org/bgframework/bgweb",
    install_requires=required
)
