from distutils.core import setup
from src import VERSION
from src import NAME

setup(
    name=NAME,
    version=VERSION,
    author='okay',
    author_email='okay.zed+pltpy@gmail.com',
    packages=[NAME],
    package_dir={NAME: 'src' },
    package_data={NAME: [
        '../README.md',
    ]},
    url='http://github.com/plaitpy/' + NAME.replace("_", "-"),
    license='MIT',
    description='a fake data inter markov process communication system',
    long_description=open('README.md').read(),
    install_requires=[ ],
    )
