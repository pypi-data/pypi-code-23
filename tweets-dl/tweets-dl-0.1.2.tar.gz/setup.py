from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='tweets-dl',
    version='0.1.2',
    author='Vaishali Garg',
    author_email='vaishaligarg@gmail.com',
    url='https://github.com/Vaishali-Garg/tweet-downloader',
    description='Download tweets as csv for a given twitter handle',
    packages=['tweet_downloader'],
    include_package_data=True,
    install_requires=[
        'requests',
    ],
    entry_points='''
        [console_scripts]
        tweets-dl=tweet_downloader.tweet_dl:main
    '''
)
