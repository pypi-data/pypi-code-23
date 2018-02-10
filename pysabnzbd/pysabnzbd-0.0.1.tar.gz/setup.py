from setuptools import setup

setup(
    name='pysabnzbd',
    packages=['pysabnzbd'],
    version='0.0.1',
    description='Python wrapper for SABnzbd API',
    author='Jerad Meisner',
    author_email='jerad.meisner@gmail.com',
    url='https://github.com/jeradM/pysabnzbd',
    download_url='https://github.com/jeradM/pysabnzbd/archive/0.0.1.tar.gz',
    keywords=['SABnzbd'],
    install_requires=[
        'aiohttp'
    ],
    classifiers=[]
)
