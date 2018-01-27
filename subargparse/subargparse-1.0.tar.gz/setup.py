from setuptools import setup
import os


def readfile(fpath):
    return open(os.path.join(os.path.abspath(os.path.dirname(__file__)), fpath), encoding='utf-8').read()


setup(
    name="subargparse",
    version="1.0",
    author="Yonatan Karidi Heller",
    author_email="ykaridi@gmail.com",
    description="A module for better handling sub-commands in argparse",
    license="MIT",
    keywords="subparser subcommand argparse",
    url="http://github.com/ykaridi/subargparse",
    download_url='https://github.com/ykaridi/subargparse/archive/1.0.tar.gz',
    long_description=readfile('README'),
    packages=['subargparse'],
    install_requires=['argparse']
)