from setuptools import setup

setup(
  name = 'lessrpc_msgpack',
  packages = ['lessrpc_msgpack'], # this must be the same as the name above
  version = '1.0.0',
  description = 'Less RPC MsgPack extension',
  author = 'Salim Malakouti',
  author_email = 'salim.malakouti@gmail.com',
  license = 'MIT',
  url = 'https://github.com/LessRPC/less_msgpack/', # use the URL to the github repo
  download_url = 'https://github.com/LessRPC/less_msgpack/archive/1.0.0.tar.gz', # I'll explain this in a second
  keywords = ['python','serialization','deserialization','rpc','rmi','less rpc', 'client', 'server'], # arbitrary keywords
  classifiers = ['Programming Language :: Python'],
  install_requires=['pylods','pylods_msgpack', 'lessrpc-common'],
)
