
from setuptools import setup


with open('readme.rst', 'r') as f:
    long_description = f.read()


setup(
    name='grapa',
    version='0.5.0.0',
    description='Grapa - graphing and photovoltaics analysis',
    author='Romain Carron',
    author_email='carron.romain@gmail.com',
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
    ],
    packages=[
        'grapa',
        'grapa.datatypes',
        'grapa.scripts',
        'grapa.gui',
    ],
    license='MIT',
    url='https://github.com/carronr/grapa/',
)
