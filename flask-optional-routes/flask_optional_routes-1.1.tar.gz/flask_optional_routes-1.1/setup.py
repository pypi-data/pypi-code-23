from distutils.core import setup
setup(
  name = 'flask_optional_routes',
  packages = ['optional_routes', 'tests'],
  include_package_data=True,
  version = '1.1',
  description = 'This library allows users to specify optional paths',
  author = 'Herbert Dawkins',
  author_email = 'DrDawkins@ClearScienceInc.com',
  url = 'https://github.com/sudouser2010/flask_optional_routes',
  download_url = 'https://github.com/sudouser2010/flask_optional_routes/archive/1.1.tar.gz',
  keywords = ['flask', 'option', 'route'],
  classifiers = [],
  python_requires='~=3.6',
  install_requires=[
  'flask==0.12.2'
  ],
)
