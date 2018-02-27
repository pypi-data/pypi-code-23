from setuptools import setup

setup(name='swdl',
      version='0.1',
      description='Soccerwatch Data Library',
      author='Christian Bodenstein',
      author_email='bodenstein@soccerwatch.tv',
      packages=['swdl'],      
      install_requires=[
          'numpy',
          'h5py',
          'tornado',
          'm3u8',
          'pydoc-markdown'
      ],
      zip_safe=False)
