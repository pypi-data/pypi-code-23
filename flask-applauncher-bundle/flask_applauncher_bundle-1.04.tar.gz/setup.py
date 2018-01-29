from distutils.core import setup
setup(
  name='flask_applauncher_bundle',
  packages=['flask_bundle'],
  version='1.04',
  description='flask support for applauncher',
  author='Alvaro Garcia Gomez',
  author_email='maxpowel@gmail.com',
  url='https://github.com/applauncher-team/flask_bundle',
  download_url='https://github.com/applauncher-team/flask_bundle/archive/master.zip',
  keywords=['flask', 'web', 'api'],
  classifiers=['Topic :: Adaptive Technologies', 'Topic :: Software Development', 'Topic :: System', 'Topic :: Utilities'],
  install_requires=['applauncher', 'Flask']
)
