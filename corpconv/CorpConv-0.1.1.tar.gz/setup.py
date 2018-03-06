# 1. Upload to PyPI:
# python3 setup.py sdist
# python3 setup.py sdist upload
#
# 2. Check if everything looks all right: https://pypi.python.org/pypi/CorpConv
#
# 3. Go to https://github.com/tsproisl/CorpConv/releases/new and
# create a new release

from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as fh:
    long_description = fh.read()

version = "0.1.1"

setup(
    name='CorpConv',
    version=version,
    author='Thomas Proisl',
    author_email='thomas.proisl@fau.de',
    packages=[
        'corpconv',
        # 'corpconv.test',
    ],
    entry_points={
        'console_scripts': ['corpconv=corpconv.cli:main'],
    },
    url="https://github.com/tsproisl/CorpConv",
    download_url='https://github.com/tsproisl/CorpConv/archive/v%s.tar.gz' % version,
    license='GNU General Public License v3 or later (GPLv3+)',
    description='A converter between various corpus formats.',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Linguistic',
    ],
)
