from setuptools import setup, find_packages

PACKAGE = "RedisQ"
NAME = "RedisQ"
DESCRIPTION = "a mini python Redis Task Queue model"
AUTHOR = "Taylor"
AUTHOR_EMAIL = "tank357@icloud.com"
URL = "https://github.com/Tsimage/RedisQ"
VERSION = "1.7.1"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description="""

    """,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    url=URL,
    packages=find_packages(),
    package_data={},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
    ],
    zip_safe=False,
    install_requires=['redis', 'pickleshare', 'click', 'pyseri', 'watchdog'],
    entry_points={
        'console_scripts': [
            'qworker=RedisQ.entry_points:cli',
            'qwatchdog=RedisQ.entry_points:watchdog',
            'qtest=RedisQ.entry_points:test',

        ],
    }

)
