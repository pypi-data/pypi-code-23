from setuptools import setup, find_packages

setup(
    name='dirgen',
    version='0.5',
    py_modules=['dirgen'],
    license="MIT",
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        dirgen=dirgen:generate_directories
    ''',
    author="Jean-Paul Fiorini",
    maintainer="Jean-Paul Fiorini"
)
