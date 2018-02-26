from setuptools import setup, find_packages

setup(
    name='pyexpress',
    version='0.1.0a4',
    description='A HTTP server framework',
    long_description='Inpired by ExpressJS, pyexpress provides a simple way to deploy a HTTP server',
    author='sdrubay',
    author_email='turtlepower@free.fr',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    url='https://github.com/drubay/pyexpress',
    keywords='http server express',
    requires=[]
)
