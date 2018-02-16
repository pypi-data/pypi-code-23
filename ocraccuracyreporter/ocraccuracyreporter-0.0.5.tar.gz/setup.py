from setuptools import find_packages, setup

from ocraccuracyreporter import __version__

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='ocraccuracyreporter',
    version=__version__,
    author='Lucid Programmer',
    author_email='lucidprogrammer@hotmail.com',
    packages=find_packages(exclude=['docs', 'tests']),
    py_modules=["oar"],
    url='https://github.com/lucidprogrammer/ocraccuracyreporter',
    license='MIT',
    description='OCR Accuracy Reporter',
    long_description=long_description,
    test_suite='tests.oar_suite',
    install_requires=[
        'python-Levenshtein',
        'fuzzywuzzy',
    ]
)
