from distutils.core import setup

setup(
    name='Converto',
    version='1.0.1',
    packages=['converto'],
    license='MIT',
    entry_points={
        'console_scripts': ['converto=converto.command_line:main'],
    },
    author='Erik Hauck',
    description="A simple, configurable wrapper for FFmpeg",
    url='https://github.com/erikmhauck/converto',
    install_requires=[
        'menu',
        'ffmpy',
        'future'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='ffmpeg wrapper configurable tool',
    project_urls={
        'Documentation': 'https://github.com/erikmhauck/converto',
        'Source': 'https://github.com/erikmhauck/converto',
        'Tracker': 'https://github.com/erikmhauck/converto/issues',
    },
    python_requires='>=2.7, <4',
    package_data={
        'converto': ['configuration/configuration.json'],
    },
)
