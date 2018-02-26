from distutils.core import setup
setup(
  name = 'dailymail_tcs',
  packages = ['dailymail_tcs'],
  version = '0.7',
  description = 'Extract title, summary and content from dailymail corpus.',
  author = 'Ajjo',
  author_email = 'ajjogames@gmail.com',
  url = 'https://github.com/ajjo/dailymail-tcs.git',
  download_url = 'https://github.com/ajjo/dailymail-tcs/archive/0.7.tar.gz',
  keywords = ['dailymail', 'title', 'summary','content'], 
  install_requires=[
    'markdown',
  ],
  classifiers = [],
)