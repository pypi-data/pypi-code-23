from setuptools import setup

setup(
    name='ravenpackapi',
    version='1.0.3',
    packages=['ravenpackapi'],
    url='https://github.com/RavenPack/python-api',
    license='MIT',
    author='RavenPack',
    author_email='dvarotto@ravenpack.com',
    description='RavenPack API - Python client',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: System :: Software Distribution',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
    ],

    keywords='python analytics api rest news data',
    install_requires=['requests[security]'],
)
