from setuptools import setup

setup(
    name='pgop',
    version='0.0.6',
    packages=['pgop'],
    install_requires=[
        'requests',
        'xmltodict',
        'urllib3',
    ],
    url='https://github.com/madmanmatt/pgop',
    license='MIT',
    author='Matt Stang',
    author_email='git@stang.im',
    description='Interface module to control Greenwave Reality Lights'
)
