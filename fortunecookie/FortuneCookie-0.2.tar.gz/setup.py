# setup.py

from setuptools import setup

setup(name='FortuneCookie',
      version='0.2',
      description='A Python package for fortune cookie phrases generation',
      url='https://github.com/carrasquel/fortune-cookie',
      author='Nelson Carrasquel',
      author_email='carrasquel.nelson@gmail.com',
      license='Apache License',
      packages=['fortune_cookie'],
      package_data={'': ['phrases.txt']},
      include_package_data=True,
      zip_safe=False)
