from distutils.core import setup
setup(
  name = 'flask_optional_routes',
  version = '1.3',
  description = 'This library allows users to specify optional paths',
  url = 'https://github.com/sudouser2010/flask_optional_routes',
  author = 'Herbert Dawkins',
  author_email = 'DrDawkins@ClearScienceInc.com',
  packages = ['flask_optional_routes'],
  include_package_data=True,

  keywords = ['flask', 'option', 'route'],
  python_requires='~=3.6',
  install_requires=[
  'flask==0.12.2'
  ],

)
