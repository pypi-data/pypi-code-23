from distutils.core import setup
setup(
  name='celery_bundle',
  packages=['celery_bundle'],
  version='1.01',
  description='celery support for applauncher',
  author='Alvaro Garcia Gomez',
  author_email='maxpowel@gmail.com',
  url='https://github.com/team',
  download_url='https://github.com/applauncher-team/celery_bundle',
  keywords=['celery'],
  classifiers=['Topic :: Adaptive Technologies', 'Topic :: Software Development', 'Topic :: System', 'Topic :: Utilities'],
  install_requires=['applauncher', 'celery']
)
