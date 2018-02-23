from setuptools import setup

setup(
    name='ct_schools',
    description="Get data about Connecticut schools",
    version='0.0.5',    
    author="Jake Kara",
    author_email="jake@jakekara.com",
    url="https://github.com/jakekara/ct_schools",
    packages=['ct_schools'],
    package_data={'ct_schools': ['data/*.csv']},
    install_requires=["fuzzywuzzy==0.16.0",
                      "pandas==0.22.0",
                      "python-Levenshtein==0.12.0"],
    license="GPL-3",
)

