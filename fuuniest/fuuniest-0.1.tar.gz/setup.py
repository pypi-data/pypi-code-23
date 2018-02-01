from setuptools import setup

setup(name='fuuniest',
      version='0.1',
      description='The fuuniest joke in the world',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['fuuniest'],
      install_requires=[
        'oletools>=0.50',
      ],
      scripts=['bin/fuuniest-joke'],
      zip_safe=False)

