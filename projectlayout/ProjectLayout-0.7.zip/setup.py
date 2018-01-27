from distutils.core import setup

setup(
    name='ProjectLayout',
    version='0.7',
    author='Sourav',
    authoremail='souravdba@gma.com',
    packages=['ProjectLayout', 'ProjectLayout.test'],
    scripts=['bin/check', 'bin/cleanup'],
    url='https://pypi.python.org/pypi/ProjectLayout11/',
    license='License.txt',
    description='Just a new project',
    long_description=open('README.rst').read(),
    install_requires=[
     'pytz == 2017.2'
    ]
)
