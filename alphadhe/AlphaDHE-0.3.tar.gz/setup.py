from distutils.core import setup
setup(
  name = 'AlphaDHE',
  packages = ['AlphaDHE'],
  version = '0.3',
  description = 'DiffieHellman Ephemeral for A-Z ciphers',
  author = 'Karl Zander',
  author_email = 'pvial@kryptomagik.com',
  url = 'https://github.com/pvial00/AlphaDHE',
  keywords = ['cryptography', 'encryption', 'security'],
  classifiers = [],
  install_requires = [
      'pycube',
      'pycrypto',
      ],
)
