from setuptools import setup

setup(
    name='pytest-gc',
    description='The garbage collector plugin for py.test',
    long_description=open('README.rst').read(),
    version='0.0.1',
    author='Victor Titor',
    author_email='vtitor.edumix@gmail.com',
    url='https://github.com/vtitor/pytest-gc',
    packages=['pytest_gc'],
    entry_points={'pytest11': ['gc = pytest_gc:PluginLoader']},
    install_requires=['pytest', 'six'],
    tests_require=['pytest'],
    classifiers=[
        'Framework :: Pytest',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6'
    ],
)
