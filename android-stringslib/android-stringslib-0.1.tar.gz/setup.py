from setuptools import setup, find_packages

setup (
    name="android-stringslib",
    version="0.1",
    packages=find_packages(exclude=['.guix-profile*']),
    data_files = [("share/doc/android-stringslib", ["_build"])],
    python_requires = '>=3',

    author="Julien Lepiller",
    author_email="julien@lepiller.eu",
    description="Android Strings Lib provides support for android's strings.xml \
files.  These files are used to translate strings in android apps.",
    license="MIT",
    keywords="android strings.xml translation",
    url="https://framagit.org/tyreunom/python-android-strings-lib",
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
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3',
],
)
