from setuptools import setup, find_packages

setup(
    name='puer',
    version='0.4.8',
    packages=find_packages(exclude=('./venv',)),
    install_requires=[
        'aiohttp',
    ],
)