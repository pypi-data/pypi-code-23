from setuptools import setup

setup(
    name='zappa-call-later',
    version='1.0.0',
    packages=['tests_project'],
    package_dir={'': 'tests/tests_project'},
    url='https://github.com/andytwoods/zappa-call-later',
    license='MIT License',
    author='andytwoods',
    author_email='andytwoods@gmail.com',
    description='tore future tasks in the db and call them after set delays'
)
