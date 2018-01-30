from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

def install_requires():
    with open("requirements.txt") as f:
        return f.readlines()


setup(
    name="debug_toolz",
    version="0.0.1",
    description="Tools to ease debugging",
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='debug tooling',
    url="https://github.com/jakab922/debug_toolz",
    download_url="https://github.com/jakab922/debug_toolz/tarball/0.0.1",
    author="Daniel Papp",
    author_email="jakab922@gmail.com",
    license="MIT",
    packages=["debug_toolz"],
    setup_requires=['pytest-runner'],
    install_requires=install_requires(),
    tests_require=['pytest'],
    include_package_data=True,
    zip_safe=False
)
