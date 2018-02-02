from setuptools import setup, find_packages

setup(
    name="mangafox-dl",
    version="1.1.5",
    description="A simple downloader for https://www.mangafox.la",
    author="Dragneel1234",
    author_email="blwal7057@gmail.com",
    url="https://github.com/Dragneel1234",
    license="GPL-3.0",
    packages=["mangafoxdl"],
    entry_points={
          'console_scripts': [
              'mangafox-dl = mangafoxdl.__main__:main'
          ]
      },
    classifiers = [
        'Environment :: Console',
        'Topic :: Utilities'
    ]
)