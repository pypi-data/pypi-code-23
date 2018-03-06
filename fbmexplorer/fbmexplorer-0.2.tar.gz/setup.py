from setuptools import setup

setup(name='fbmexplorer',
      version='0.2',
      description='Parser to extract Facebook Messenger Data, and explorer it on d3.js tool.',
      url='https://github.com/adurivault/FBMessage',
      author='adurivault, MathReynaud',
      author_email='a.durivault@gmail.com, mathild.reynaud@gmail.com',
      license='MIT',
      install_requires=[
          'fbchat-archive-parser',
          'pandas',
      ],
      scripts=['bin/fbm-parse'],
      packages=['fbmexplorer'],
      zip_safe=False)
