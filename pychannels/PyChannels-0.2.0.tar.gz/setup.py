from distutils.core import setup

setup(
    name='PyChannels',
    version='0.2.0',
    packages=['pychannels',],
    license='The MIT License',
    long_description=open('README.md').read(),
    description = 'API client for the Channels app - https://getchannels.com',
    author = 'Fancy Bits, LLC',
    author_email = 'jon@getchannels.com',
    url = 'https://github.com/fancybits/pychannels',
    keywords = ['api', 'client', 'channels', 'automation'],
    install_requires = ['requests'],
)
