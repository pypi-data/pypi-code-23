from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install


class DevelopCommand(develop):
    def run(self):
        raise Exception("The correct pip package to install is 'django-television' (not 'television').")
        develop.run(self)


class InstallCommand(install):
    def run(self):
        raise Exception("The correct pip package to install is 'django-television' (not 'television').")
        install.run(self)


setup(
    cmdclass={
        'develop': DevelopCommand,
        'install': InstallCommand,
    },
    name='television',
    version='0.1.1',
    packages=['television'],
    scripts=[],
    install_requires=[
        'Django>=1.11',
        'channels==1.1.8'
    ],
    author='Patrick Paul',
    author_email='patrick@astrohaus.com',
    description='Back-end Python utilities for use with Django Channels',
    license='MIT',
    # keywords='',
    url='https://github.com/pztrick/django-television/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
