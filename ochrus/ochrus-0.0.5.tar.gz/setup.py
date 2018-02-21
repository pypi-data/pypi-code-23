from distutils.core import setup
setup(
  name = 'ochrus',
  packages = ['ochrus'], # this must be the same as the name above
  license = 'MIT',
  version = '0.0.5',
  description = 'Ochrus functional test automation infrastructure',
  long_description=open('README.rst').read(),
  author = 'Roni Eliezer',
  author_email = 'roniezr@gmail.com',
  url = 'https://github.com/ochrus/ochrus', # use the URL to the github repo
  download_url = 'https://github.com/ochrus/ochrus-0.0.5.tar.gz',
  keywords = ['functional', 'testing', 'automation', 'infrastructure'], 
  classifiers = [],
  install_requires=['paramiko', 'requests'],
)