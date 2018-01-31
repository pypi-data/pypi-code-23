from setuptools import setup

setup(  
    name="tQuotes",
    version='0.0.3',
    description = 'A library to get quotes from www.goodread.com.',
    long_description="A library to get quotes from www.goodread.com and maybe another websites later, maybe... maybe not.",
    author="Erik Ochoa",
    author_email="elyager@gmail.com",
    url="https://github.com/Elyager/tQuotes",
    license="MIT",
    # package_dir={'tQuotes': 'tQuotes'},
    # py_modules=['good_reads'],
    packages=['quotes'],
    install_requires=[
        'beautifulsoup4==4.6.0',
        'requests==2.18.4'
    ],
    # entry_points='''
    #     [console_scripts]
    #     good_reads=good_reads:generate_quote
    # '''
)