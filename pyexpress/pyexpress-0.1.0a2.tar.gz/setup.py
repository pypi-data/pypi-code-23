from setuptools import setup, find_packages

setup(
    name='pyexpress',
    version='0.1.0a2',
    description='A HTTP server framework',
    author='sdrubay',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    keywords='http server express',
    project_urls={
        'Source': 'https://github.com/drubay/pyexpress'
    }
)
