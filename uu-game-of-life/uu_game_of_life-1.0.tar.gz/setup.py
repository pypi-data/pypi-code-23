from setuptools import setup


setup(
    name = 'uu_game_of_life',
    version='1.0',
    description='Example package of game of life',
    url='https://github.com/Hakanwie/uu-gol.git',
    author='Håkan Wieslander',
    author_email='hakan.wieslander@it.uu.se',
    py_modules=['gol'],
    install_requires=[
          'numpy',
          'scipy'
      ],
    packages=[])