from setuptools import setup

setup(  
    name="tQuotes",
    version='0.0.4',
    description = 'A library to get quotes from www.goodread.com.',
    long_description="A library to get quotes from www.goodread.com and maybe another websites later, maybe... maybe not.",
    author="Erik Ochoa",
    author_email="elyager@gmail.com",
    url="https://github.com/Elyager/tQuotes",
    license="MIT",
    packages=['quotes'],
    install_requires=[
        'beautifulsoup4==4.6.0',
        'requests==2.18.4'
    ]
)