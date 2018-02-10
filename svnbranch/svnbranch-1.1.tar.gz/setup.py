from setuptools import setup

dic = {}
exec(open('svnbranch/svnbranch.py').read(), dic)
VERSION = dic['__version__']


if __name__ == '__main__':
    setup(name='svnbranch',
          version=VERSION,
          description='A simple svn branch tool with externals support',
          long_description=open('README.rst').read(),
          author='fyrestone',
          author_email='fyrestone@outlook.com',
          url='https://github.com/fyrestone/svnbranch',
          license="MIT License",
          packages=['svnbranch'],
          keywords="svn branch external generic utility",
          platforms=["All"],
          classifiers=['Development Status :: 5 - Production/Stable',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: MIT License',
                       'Natural Language :: English',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python :: 2',
                       'Programming Language :: Python :: 3',
                       'Topic :: Software Development :: Libraries',
                       'Topic :: Utilities'],
          entry_points={
              'console_scripts': [
                  'svnbranch = svnbranch:main',
              ],
          },
          install_requires=['gevent', 'url-normalize', 'six'],
          test_suite='tests',
          zip_safe=False)
