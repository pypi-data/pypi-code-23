from setuptools import setup

setup(name='unipy_logger',
      keywords='log, json, uniplaces',
      version='0.1.8',
      description='enforce uniplaces log standards and respect uniplaces logging interface.',
      url='https://github.com/uniplaces/unipy_logger',
      author='Raffaello De Pieri',
      author_email='raffaello.pieri@uniplaces.com',
      license='MIT',
      packages=['unipy_logger'],
      install_requires=['logbook'],
      zip_safe=False)
