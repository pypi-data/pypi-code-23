from setuptools import setup, find_packages

setup(
    name='puer_rest',
    version='0.1.1',
    packages=find_packages(exclude=('./venv',)),
    install_requires=[
        'puer',
    ],
)