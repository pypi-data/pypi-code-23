from distutils.core import setup

setup(
  name = 'nnpush',
  packages = ['nnpush'], # this must be the same as the name above
  version = '0.2',
  description = 'A library to hook into neural network training iterations so it can be monitored from the mobile app NNPush and be notified when training is complete!',
  author = 'Richard Fox',
  author_email = 'fox.ios.dev@gmail.com',
  url = 'http://deepdescent.net', # use the URL to the github repo
  keywords = ['neural network', 'monitor', 'training', 'deep learning', 'nnpush', 'nueral', 'network'], # arbitrary keywords
  classifiers = []
)