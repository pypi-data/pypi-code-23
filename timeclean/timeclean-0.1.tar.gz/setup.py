#from distutils.core import setup
from setuptools import setup

setup(
    name = 'timeclean',
    version = '0.1',
    description = 'Python package to help set up time series data for machine learning',
    author = 'Dinesh K Rai',
    url = 'https://github.com/DineshRai/timecleaner', 
    py_modules=['timecleaner'],
    license='MIT',
    install_requires=[
        "numpy",
        "pandas"
    ]
)