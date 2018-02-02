from setuptools import setup, find_packages

setup(
    name='puer',
    version='0.4.9',
    packages=find_packages(exclude=('./venv',)),
    install_requires=[
        'aiohttp',
    ],
)