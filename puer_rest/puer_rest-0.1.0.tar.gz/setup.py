from setuptools import setup, find_packages

setup(
    name='puer_rest',
    version='0.1.0',
    packages=find_packages(exclude=('./venv',)),
    install_requires=[
        'puer',
    ],
)