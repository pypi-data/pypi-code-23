from setuptools import setup

setup(
    # This is the name of your PyPI-package.
    name='norwegian-adresses',
    version='0.2',                          # Update the version number for new releases
    # The name of your scipt, and also the command you'll be using for calling it
    author="Runar Kristoffersen",
    author_email="runar@rkmedia.no",
    url="https://github.com/runar-rkmedia/addresses",
    packages=['norwegian_adresses'],
    install_requires=[
        "pymongo>=3.4.0",
    ]

)
