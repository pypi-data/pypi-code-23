from setuptools import setup

setup(
    # This is the name of your PyPI-package.
    name='norwegian-adresses',
    version='0.1.01',                          # Update the version number for new releases
    # The name of your scipt, and also the command you'll be using for calling it
    author="Runar Kristoffersen",
    author_email="runar@rkmedia.no",
    url="https://github.com/runar-rkmedia/addresses",
    packages=['norwegian_adresses'],
    install_requires=[
        "nose2==0.6.5",
        "psycopg2==2.7.1",
        "pymongo==3.4.0",
        "six==1.10.0",
        "SQLAlchemy==1.1.10",
        "utm==0.4.2",
    ]

)
