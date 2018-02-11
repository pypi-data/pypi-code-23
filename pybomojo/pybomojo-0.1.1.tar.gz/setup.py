from distutils.core import setup

setup(
    name='pybomojo',
    packages=['pybomojo'],
    version='0.1.1',
    description='Python client for boxofficemojo.com',
    install_requires=[
        'beautifulsoup4>=4.6.0,<5',
        'requests>=2.18.1,<3',
    ],
    author='Dan Tao',
    author_email='daniel.tao@gmail.com',
    url='https://bitbucket.org/dtao/pybomojo',
    keywords=[],
    classifiers=[],
)
