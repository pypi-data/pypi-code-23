import os
import re
import sys
from setuptools import setup


if sys.hexversion < 0x3040000:
    msg = "Python version %s is unsupported, >= 3.4.0 is needed"
    print(msg % (".".join(map(str, sys.version_info[:3]))))
    exit(1)


# with open("README.md", "rt") as f:
#     readme = f.read()


setup(name='text2pdf',
      version='0.1',
      description='Tools to convert text files to PDF',
      long_description='',
      url='https://github.com/tedlaz/text2pdf',
      keywords=["PDF", "gui", "pyqt5"],
      author='Ted Lazaros',
      author_email='tedlaz@gmail.com',
      install_requires=['PyQt5'],
      license='GPLv3',
      packages=['text2pdf'],
      scripts=['text2pdf/text2pdf', 'text2pdf/text2pdfgui'],
      package_data={'text2pdf': ['templates/images/*.png', 'templates/*.*']},
      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: Console",
                   "Environment :: X11 Applications :: Qt",
                   "Environment :: Win32 (MS Windows)",
                   "Intended Audience :: Developers",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3 :: Only",
                   "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.6",
                   "Topic :: Software Development :: Build Tools"]
      )
