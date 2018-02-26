from distutils.core import setup
setup(
  name = 'dailymail_tcs',
  packages = ['dailymail_tcs'],
  version = '0.8',
  description = 'Extract title, summary and content from dailymail corpus.',
  author = 'Ajjo',
  author_email = 'ajjogames@gmail.com',
  url = 'https://github.com/ajjo/dailymail-tcs.git',
  keywords = ['dailymail', 'title', 'summary','content'], 
  install_requires=[
    'BeautifulSoup',
  ],
  classifiers = [],
)