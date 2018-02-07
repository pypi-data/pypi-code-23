from setuptools import setup

setup(
    name = 'pyTrivialFTP',
    version = '0.3.0',
    description = "The poor man's API for accessing data on a remote FTP repository",
    packages = [ 'pyTrivialFTP' ],
    author = 'Roberto Reale',
    author_email = 'rober.reale@gmail.com',
    url = 'https://github.com/robertoreale/pyTrivialFTP',
    keywords = [ 'FTP' ],
    install_requires = [ ],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    entry_points={
        'console_scripts': [
            'pyTrivialFTP = pyTrivialFTP.__main__:main'
            ]
        },
)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
