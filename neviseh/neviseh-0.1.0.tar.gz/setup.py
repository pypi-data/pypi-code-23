import re
from os.path import join, dirname
from setuptools import setup, find_packages
readme = open('README.rst').read()

# reading package version (without reloading it)
with open(join(dirname(__file__), 'neviseh', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)

setup(
    name='neviseh',
    description='Simple text processing tools in persian',
    long_description=readme,
    version=package_version,
    author='Mahdi Ghane.g',
    license='MIT',
    keywords='text-processing persian iran localization',
    url='https://github.com/meyt/neviseh',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Natural Language :: Persian',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing'
    ],
    packages=find_packages()
)
