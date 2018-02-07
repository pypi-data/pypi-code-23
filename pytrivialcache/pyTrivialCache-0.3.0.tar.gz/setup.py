from setuptools import setup

setup(
    name = 'pyTrivialCache',
    version = '0.3.0',
    description = "The poor man's API for manipulating a file system cache.",
    packages = [ 'pyTrivialCache' ],
    author = 'Roberto Reale',
    author_email = 'rober.reale@gmail.com',
    url = 'https://github.com/robertoreale/pyTrivialCache',
    keywords = [ 'filesystem', 'cache' ],
    install_requires = [ ],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    entry_points={
        'console_scripts': [
            'pyTrivialCache = pyTrivialCache.__main__:main'
            ]
        },
)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
