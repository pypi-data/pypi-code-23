from distutils.core import setup

DESCRIPTION = """
Generic libraries for personal use: this is a collection of scripts
 and utilities I developed over the years and to
which I keep coming back.
"""

setup(
    name='iz4vve',
    version='0.1.5',
    packages=['utils', "spectral_analysis", "probabilistic"],
    license='GNU GPL3',
    long_description=DESCRIPTION,
    author="Pietro Masccolo",
    author_email="iz4vve@gmail.com"
)
