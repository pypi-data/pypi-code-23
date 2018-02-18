from setuptools import setup, find_packages

setup (
    name="transmon",
    version="0.1",
    packages=find_packages(exclude=['.guix-profile*']),
    python_requires = '>=3',
    install_requires=['android-stringslib', 'polib', 'pygit2'],
    entry_points={
    'console_scripts': [
        'transmon=transmon:main',
    ],
    },

    author="Julien Lepiller",
    author_email="julien@lepiller.eu",
    description="Translation monitor",
    long_description="Transmon is a translation monitor.  It uses a manifest \
that lists projects you are interested in.  It will get the latest release or \
development version (e.g. latest git commit) and try to find localisation \
information in the project.",
    license="AGPLv3+",
    keywords="translation monitor",
    url="https://framagit.org/tyreunom/transmon",
    classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Localization',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3',
],
)
