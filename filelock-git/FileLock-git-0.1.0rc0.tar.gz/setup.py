from distutils.core import setup

setup(
    name='FileLock-git',
    version='0.1.0rc0',
    author='Evan Fosmark',
    author_email='me@evanfosmark.com',
    packages=['filelock_git'],
    url='https://github.com/dmfrey/FileLock',
    license='LICENSE.txt',
    description='File locking library',
    long_description=open('README.txt').read()
)
