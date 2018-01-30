from distutils.core import setup
setup(
  name = 'cryptoenv',
  packages = ['cryptoenv', 'cryptoenv.components'],
  package_data = {
      'cryptoenv': ['env.py'],
      'cryptoenv.components': ['*'],
      },
  version = '0.1.5',
  description = 'A random test lib',
  author = 'Luthfi Mahendra',
  author_email = 'luthfimaa@gmail.com',
  url = 'https://gitlab.com/luthfimaa/cryptoenv/',
  download_url = 'https://gitlab.com/luthfimaa/cryptoenv/repository/0.1.5/archive.tar.gz', 
  keywords = [],
  classifiers = [],
)
