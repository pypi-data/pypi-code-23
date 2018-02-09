from setuptools import setup, find_packages
setup(
  name = 'FQTool',
  packages=find_packages("."),
  version = '1.1',
  description = 'Tool to parse and filter FASTQ files',
  author = 'Matteo Mistri, Bruno Palazzi, Lorenzo Soligo',
  author_email = 'slg.lnz96@icloud.com',
  license = 'GNU GPLv3',
  url = 'https://github.com/mistrello96/FQTool', # use the URL to the github repo
  download_url = 'https://github.com/mistrello96/FQTool/archive/1.0.tar.gz', # I'll explain this in a second
  keywords = ['fastq', 'read', 'bioinformatics', 'parser'], # arbitrary keywords
  classifiers = [],
)
