from setuptools import setup

setup(name='lrs',
      version='0.1.1',
      description='Save you training data online',
      url='https://learning-rates.com',
      author='Ilya Ovdin',
      author_email='iovdin@gmail.com',
      license='Apache License 2.0',
      entry_points = {
        'console_scripts': ['lrs=lrs:main'],
      },
      install_requires = {
        'requests'
      },
      packages=['lrs'],
      zip_safe=False)
