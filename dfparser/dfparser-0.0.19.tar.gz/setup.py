"""Dataforge parser setup script."""
from pip.req import parse_requirements
from setuptools import find_packages, setup

INSTALL_REQS = parse_requirements("dfparser/requirements.txt",
                                  session='hack')
REQS = [str(ir.req) for ir in INSTALL_REQS]

setup(
    name='dfparser',
    packages=find_packages(),
    version='0.0.19',
    description='Parser for dataforge-envelope (http://npm.mipt.ru/'
    'dataforge/) format.',
    author='Vasilii Chernov',
    author_email='kapot65@gmail.com',
    url='https://github.com/kapot65/python-df-parser',
    download_url='https://github.com/kapot65/python-df-parser/tarball/0.0.19'
    'master.zip',
    keywords=['dataforge', 'parser'],
    install_requires=REQS,
    include_package_data=True,
    package_data={
        '': ['*.proto'],
    },
    classifiers=[],
)
