from distutils.core import setup

with open('README.rst', 'r') as f:
    long_description = f.read()
with open('version.txt', 'r') as f:
    version = f.read().strip()

classifiers=[
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License'
]

#FIXME add more arguments https://packaging.python.org/tutorials/distributing-packages/#setup-args
setup(
  name='singular_api',
  packages=['singular_api', 'singular_api.models'],
  version=version,
  license='MIT',
  description='Singular-center python API',
  long_description=long_description,
  author='Websensa',
  author_email='websensa@websensa.com',
  url='http://websensa.com',
  download_url='http://websensa.com',
  keywords=['api', 'singular', 'time managment'],
  classifiers=classifiers,
  install_requires=['requests'],
  python_requires='>=3'
)