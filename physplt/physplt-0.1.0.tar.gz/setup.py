from setuptools import setup

setup(name='physplt',
      version='0.1.0',
      description='A collection of functions to obscure the matplotlib code needed to plot standard physics graphs',
      url='https://github.com/kaumaron/physplt',
      author='Andrew DeCotiis-Mauro',
      author_email='andrew.decotiis.mauro@gmail.com',
      license='GPL-3.0+',
      packages=['physplt'],
      install_requires=[
          'matplotlib',
      ],
      zip_safe=False)
