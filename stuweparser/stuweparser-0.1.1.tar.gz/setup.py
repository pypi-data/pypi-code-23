from setuptools import setup, Extension

pkg = __import__('stuweparser')

author =  pkg.__author__
email = pkg.__author_email__

version = pkg.__version__
classifiers = pkg.__classifiers__

description = pkg.__description__

def load_requirements(fn):
    """Read a requirements file and create a list that can be used in setup."""
    with open(fn, 'r') as f:
        return [x.rstrip() for x in list(f) if x and not x.startswith('#')]


ext_modules = []
cmdclass = {}

setup(
    name='stuweparser',
    version=version,
    license='MIT',
    description=description,
    long_description=open('README.rst').read(),
    author=author,
    author_email=email,
    url='https://github.com/Trybnetic/stuweparser',
    classifiers=classifiers,
    platforms='Linux',
    packages=['stuweparser'],
    install_requires=load_requirements('requirements.txt'),
    ext_modules=ext_modules,
    cmdclass=cmdclass
)
