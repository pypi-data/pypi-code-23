from setuptools import setup

__version__ = ['0.4']

setup(name='pullboy',
      version='.'.join(__version__),
      description='Super Simply Auto-Deployment server',
      url='http://gitlab.com/theSage21/pullboy',
      author='Arjoonn Sharma',
      author_email='arjoonn.94@gmail.com',
      packages=['pullboy'],
      install_requires=['bottle', 'pyyaml'],
      entry_points={'console_scripts': ['pullboy=pullboy:main']},
      keywords=['pullboy', 'auto deploy server'],
      zip_safe=False)
