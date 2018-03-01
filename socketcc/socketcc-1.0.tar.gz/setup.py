from distutils.core import setup

setup(
    name='socketcc',
    packages=['socketcc'],  # this must be the same as the name above
    version='1.0',
    description='Python client for socket-cluster (http://socketcluster.io)',
    long_description='This is a refined fork of https://github.com/sacOO7/socketcluster-client-python',
    author='Ramazan Polat',
    author_email='ramazanpolat@gmail.com',
    url='https://github.com/ramazanpolat/socketcc',
    download_url='https://pypi.python.org/pypi/socketcc',
    keywords=['socketcluster', 'socket-cluster', 'python3'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Software Development :: Libraries :: Python Modules'],
    install_requires=['websocket-client']
)
