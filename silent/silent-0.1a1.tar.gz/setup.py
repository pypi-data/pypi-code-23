from setuptools import setup

setup(
    name='silent',
    version='0.1a1',
    packages=['silent'],
    url='https://github.com/vinyasns/silent',
    license='GPLv3',
    author='Vinyas N S',
    author_email='vinyasns@gmail.com',
    description='A commandline client for file.io',
    install_requires=['clint', 'python-magic', 'requests_toolbelt'],
    python_requires='>=3',
    keywords=['file.io', 'commandline', 'utilities', 'anonymous'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'silent=silent.silent:main',
        ],
    },
)
