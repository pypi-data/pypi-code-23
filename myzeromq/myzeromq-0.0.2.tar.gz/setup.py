from setuptools import setup
 

 
# specify requirements of your package here
REQUIREMENTS = ['google.protobuf.json_format','json','zmq','sys',]
 
# some more details
CLASSIFIERS = [
    'Programming Language :: Python :: 3.5',
    ]
 
# calling the setup function 
setup(name='myzeromq',
      version='0.0.2',
      description='A request and response by using port',
      url='https://github.com/arockiastanlya/myzeromq',
      author='arockia stanly a',
      author_email='stanly499@gmail.com',
      packages=['zeromq'],
      classifiers=CLASSIFIERS,
      install_requires=REQUIREMENTS
      )