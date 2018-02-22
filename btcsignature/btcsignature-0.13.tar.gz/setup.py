from setuptools import setup

setup(name='btcsignature',
      version='0.13',
      description='secure offline bitcoin transaction signing tool',
      url='http://github.com/superarius/sendbtcsimply/',
      author='sendbtcsimply',
      author_email='sendbtcsimply@protonmail.com',
      license='MIT',
      packages=['btcsignature'],
      entry_points = {'console_scripts': ['sign-offline=btcsignature.command_line:main', 'read-tx=btcsignature.command_line:m2'],},
      install_requires=['bitcoin==1.1.42','blockchain', 'enum', 'ecdsa'],
      zip_safe=False)