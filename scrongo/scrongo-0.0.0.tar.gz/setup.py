from setuptools import setup

setup(
    name='scrongo',
    version='0.0.0',
    description='Non-blocking ItemExporter for MongoDB',
    url='https://github.com/lthibault/scrongo',
    author='Louis Thibault',
    author_email='l.thibault@sentimens.com',
    license='MIT',
    packages=['scrongo'],
    install_requires=["scrapy"],
    keywords=["scrapy", "mongo", "mongodb", "mongo", "nosql", "async", "nonblocking", "twisted"],
    zip_safe=True,
)
