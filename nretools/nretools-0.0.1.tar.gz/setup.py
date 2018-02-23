from __future__ import print_function
from setuptools import setup, find_packages
import io

if __name__ == "__main__":

    # from http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
    def read(*file_names, **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        sep = kwargs.get('sep', '\n')
        buf = []
        for filename in file_names:
            with io.open(filename, encoding=encoding) as f:
                buf.append(f.read())
        return sep.join(buf)

    long_description = read('README.txt')

    setup(
        name="nretools",
        # MAJOR version when they make incompatible API changes,
        # MINOR version when they add functionality in a backwards-compatible manner, and
        # MAINTENANCE version when they make backwards-compatible bug fixes.
        # http://semver.org/
        version="0.0.1",
        packages=find_packages(),
        license='MIT',
        author='Tyler Weirick', author_email='tyler.weirick@gmail.com',
        description='A software package for finding differential A-to-I editing.',
        long_description=long_description,
        platforms='any',
        scripts=['nretools'],
        install_requires=[
            # Used with the program.
            'intervaltree>=2.1.0',
            # For testing.
            # 'behave',
            # 'mock'
        ]
    )

