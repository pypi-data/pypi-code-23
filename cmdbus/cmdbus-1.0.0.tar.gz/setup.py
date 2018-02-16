from distutils.core import setup

github = 'https://github.com/jmwri/cmdbus'
version = '1.0.0'

setup(
    name='cmdbus',
    packages=['cmdbus'],
    version=version,
    license='MIT',
    python_requires='>=3.6, <4',
    description='A simple command bus.',
    author='Jim Wright',
    author_email='jmwri93@gmail.com',
    url=github,
    download_url='{github}/archive/{version}.tar.gz'.format(
        github=github, version=version
    ),
    keywords=['command', 'bus'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)
