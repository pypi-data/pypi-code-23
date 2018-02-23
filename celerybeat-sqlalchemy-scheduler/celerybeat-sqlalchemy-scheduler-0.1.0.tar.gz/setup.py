import os

from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='celerybeat-sqlalchemy-scheduler',
    version='0.1.0',
    packages=find_packages('src', exclude=('tests',)),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    description=(
        'Python IMDB client using the IMDB json web service made '
        'available for their iOS app.'
    ),
    author='Richard O\'Dwyer',
    author_email='richard@richard.do',
    license='Apache 2',
    long_description=(
        'https://github.com/richardasaurus/celerybeat-sqlalchemy-scheduler'
    ),
    install_requires=install_requires,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
