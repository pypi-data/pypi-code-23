from setuptools import setup

setup(
    name = 'gossipy',
    version = '0.1',
    description = 'A basic chat class',
    packages = [ 'gossipy' ],
    author = 'Roberto Reale',
    author_email = 'rober.reale@gmail.com',
    url = 'https://github.com/robertoreale/gossipy',
    keywords = [ 'chat' ],
    install_requires = [  ],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
