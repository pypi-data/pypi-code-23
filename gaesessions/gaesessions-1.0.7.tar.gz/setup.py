from setuptools import setup
setup(name='gaesessions',
      version='1.0.7',
      author='Eirik Tenold',
      author_email='eirik@relativt.net',
      license='Apache License Version 2.0',
      url='https://github.com/lagren/gae-sessions',
      description='gae-sessions is a sessions library for the Python runtime on Google App Engine for ALL session sizes. ' +
                  'It is extremely fast, lightweight (one file), and easy to use. This is a packed version of the inactive project at https://github.com/dound/gae-sessions',
      py_modules=['gaesessions.__init__'],
      install_requires=[
      ])