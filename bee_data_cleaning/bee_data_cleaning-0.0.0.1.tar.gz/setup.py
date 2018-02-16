from setuptools import setup, find_packages

setup(
    name='bee_data_cleaning',
    version='0.0.0.1',
    packages=find_packages(),
    url='https://github.com/BeeGroup-cimne/bee_data_cleaning',
    license='MIT',
    author='BEE Group - CIMNE',
    author_email='egabaldon@cimne.upc.edu',
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'plotly'
    ],
    description='Data cleaning for building energy and temperature timeseries.',
    test_suite='nose.collector',
    tests_require=['nose'],
)