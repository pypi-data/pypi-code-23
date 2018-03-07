from distutils.core import setup
setup(
  name='mongoengine_bundle',
  packages=['mongoengine_bundle'],
  version='1.0',
  description='mongoengine support for applauncher',
  author='Alvaro Garcia Gomez',
  author_email='maxpowel@gmail.com',
  url='https://github.com/applauncher-team/mongoengine_bundle',
  download_url='https://github.com/applauncher-team/mongoengine_bundle/archive/master.zip',
  keywords=['mongoengine', 'applauncher'],
  classifiers=['Topic :: Adaptive Technologies', 'Topic :: Software Development', 'Topic :: System', 'Topic :: Utilities'],
  install_requires=['applauncher', 'mongoengine']
)
