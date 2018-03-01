from setuptools import setup, find_packages

setup(
    name='mypc',
    version='0.0.1',
    description='Open "This PC" on Windows.',
    url='https://github.com/Frederick-S/mypc',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'mypc = mypc.main:main'
        ]
    },
    include_package_data=True,
    test_suite="tests"
)
