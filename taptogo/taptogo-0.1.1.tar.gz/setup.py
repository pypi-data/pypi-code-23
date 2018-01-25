from setuptools import setup

setup(
    name='taptogo',
    packages=['taptogo'],
    version = "0.1.1",
    author = 'Brandon Telle',
    author_email = 'brandon.telle@gmail.com',
    url = 'https://github.com/btelle/taptogo',
    download_url = 'https://github.com/btelle/taptogo/archive/0.1.1.tar.gz',
    include_package_data=True,
    install_requires=[
        'selenium',
        'BeautifulSoup4'
    ],
)
