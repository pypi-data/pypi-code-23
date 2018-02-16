
from distutils.core import setup

setup(name='Flask-Builder',
      version='0.9',
      description='Flask-application factory',
      author='Y-Bro',
      url='https://github.com/n0nSmoker/flask_builder',
      keywords=['flask', 'builder'],
      packages=['flask_builder'],
      install_requires=[
        'flask',
        'SQLAlchemy',
        'Flask-SQLAlchemy',
        'Flask-Migrate',
        'Flask-Mail',
        'raven',
        'blinker',
      ]
     )
