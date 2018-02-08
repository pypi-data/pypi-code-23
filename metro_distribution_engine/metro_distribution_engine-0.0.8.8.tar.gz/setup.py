from distutils.core import setup

setup(
    name="metro_distribution_engine",
    version="0.0.8.8",
    url="https://metro.exchange",
    description="The distribution engine for moving metrics around the metro network",
    author="Rory Byrne",
    author_email="rory.byrne57@mail.dcu.ie",
    packages=['metro_distribution_engine', 'metro_distribution_engine/sqs_engine']
)
