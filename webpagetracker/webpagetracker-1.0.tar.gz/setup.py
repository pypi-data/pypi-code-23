from setuptools import setup

setup(name = 'webpagetracker',
      version = '1.0',
      description = 'Track web pages and inform changes through email',
      long_description = 'Track web pages and inform changes through email',
      url = 'http://github.com/cjlcarvalho/webpagetracker',
      author = 'Caio Jordão Carvalho',
      author_email = 'caiojcarvalho@gmail.com',
      license = 'LGPL',
      keywords = 'webpagetracker webtracker tracker web scraper',
      packages = ['webpagetracker'],
      install_requires = [
          'requests',
      ],
      zip_safe = False,
      python_requires = '>=3')
