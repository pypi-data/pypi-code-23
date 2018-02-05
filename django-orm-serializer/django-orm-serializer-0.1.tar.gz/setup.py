from distutils.core import setup
setup(
  name = 'django-orm-serializer',
  scripts = ['ormserializer.py'], # this must be the same as the name above
  version = '0.1',
  description = 'This serializer support django orm data to python object',
  author = 'Sefa Akgumus',
  author_email = 'sefisakgms@gmail.com',
  url = 'https://github.com/sefoli/', # use the URL to the github repo
  download_url = 'https://github.com/sefoli/django-orm-serializer/archive/master.zip', # I'll explain this in a second
  keywords = ['django', 'serializer', 'json', 'xml'], # arbitrary keywords
  classifiers = [],
)
