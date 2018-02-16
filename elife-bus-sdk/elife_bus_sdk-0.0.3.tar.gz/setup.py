from setuptools import setup

import elife_bus_sdk


DEFAULT_DEPENDENCIES = (
    'boto3==1.4.7',
)


try:
    with open('requirements.txt') as requirements_file:
        DEPENDENCIES = requirements_file.readlines()
except FileNotFoundError:
    DEPENDENCIES = DEFAULT_DEPENDENCIES


setup(
    name='elife_bus_sdk',
    version=elife_bus_sdk.__version__,
    description='This library provides a Python SDK for the eLife Sciences Bus',
    packages=['elife_bus_sdk'],
    include_package_data=True,
    install_requires=DEPENDENCIES,
    license='MIT',
    url='https://github.com/elifesciences/bus-sdk-python.git',
    maintainer='eLife Sciences Publications Ltd.',
    maintainer_email='tech-team@elifesciences.org',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
    ]

)

