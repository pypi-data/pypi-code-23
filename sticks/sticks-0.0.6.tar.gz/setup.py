import os
from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    long_description = readme_file.read()

setup(  
    name="sticks",
    packages=find_packages(),
    version='0.0.6',
    description="Simple game application.",
    long_description=long_description,
    author="ganeshhubale.",
    author_email="ganeshhubale03@gmail.com",
    url="https://github.com/ganeshhubale/game_of_sticks",
    license="MIT",
    py_modules=['sticks.__init__'],
    namespace_packages=[],
    entry_points={
        'console_scripts': [
            'sticks = sticks.__init__:main',
        ],
    },
)
