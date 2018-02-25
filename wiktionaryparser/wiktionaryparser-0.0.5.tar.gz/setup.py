from setuptools import setup,find_packages

setup(
  name = 'wiktionaryparser',
  version = '0.0.5',
  description = 'A tool to parse word data from wiktionary.com into a JSON object',
  packages = ['wiktionaryparser'],
  author = 'Suyash Behera',
  author_email = 'sne9x@outlook.com',
  url = 'https://github.com/Suyash458/WiktionaryParser', 
  download_url = 'https://github.com/Suyash458/WiktionaryParser/archive/master.zip', 
  keywords = ['Parser', 'Wiktionary'],
  install_requires = ['beautifulsoup4','requests'],
  classifiers=[
   'Development Status :: 5 - Production/Stable',
    ],
)