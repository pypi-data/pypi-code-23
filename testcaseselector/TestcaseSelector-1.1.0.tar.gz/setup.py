from distutils.core import setup
from pkgutil import walk_packages
import TestcaseSelect

def find_packages(path='.', prefix=""):
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name

setup(
  name = 'TestcaseSelector',
  packages = list(find_packages(TestcaseSelect.__path__, TestcaseSelect.__name__)),
  version = '1.1.0',
  description = 'Unittest test selector window',
  author = 'Charles Whaples',
  author_email = 'whaplescr@gmail.com',
  url = 'https://github.com/Whaplescr/TestcaseSelector',
  download_url = 'https://github.com/Whaplescr/TestcaseSelector/tarball/1.1.0',
  keywords = ['appium', 'selenium', 'testing','unittest','tkinter','ttk'],
  classifiers=[],
  install_requires=[]
)