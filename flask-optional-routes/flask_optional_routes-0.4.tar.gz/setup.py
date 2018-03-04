from distutils.core import setup
setup(
  name = 'flask_optional_routes',
  packages = ['flask_optional_routes'],
  version = '0.4',
  description = 'This library allows users to specify optional paths',
  author = 'Herbert Dawkins',
  author_email = 'DrDawkins@ClearScienceInc.com',
  url = 'https://github.com/sudouser2010/flask_optional_routes',
  download_url = 'https://github.com/sudouser2010/flask_optional_routes/archive/0.4.tar.gz',
  keywords = ['fl4sk', 'option', 'route'],
  classifiers = [],
  python_requires='~=3.6',
  install_requires=[
  'flask==0.12.2'
  ],
)
