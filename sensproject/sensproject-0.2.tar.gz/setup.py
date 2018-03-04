from setuptools import setup
import os

datadir = os.path.join('sensproject/skel')
datafiles = [(d, [os.path.join(d,f) for f in files])
    for d, folders, files in os.walk(datadir)]

setup(
  name = 'sensproject',
  packages = ['sensproject'],
  version = '0.2',
  description = 'A simple script to create new Senscape project',
  author = 'Guillem Castro',
  author_email = 'guillemcastro4@gmail.com',
   data_files=datafiles,
  entry_points={
        'console_scripts': [
            'sensproj = sensproject.projectcreator:main',
        ],
    }
)