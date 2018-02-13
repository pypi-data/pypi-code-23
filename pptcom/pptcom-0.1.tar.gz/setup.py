import os
from setuptools import setup


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    long_description = open('README.md').read()

setup(
    author='Marco Rossi',
    author_email='developer@marco-rossi.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    description='Use Microsoft PowerPoint within Python with the help of COM',
    extras_require={'test': ['pytest', 'python-pptx']},
    install_requires=['comtypes'],
    keywords=['com', 'powerpoint'],
    license='MIT',
    long_description=long_description,
    name='pptcom',
    packages=['pptcom'],
    python_requires='>=3.6',
    url='https://github.com/m-rossi/pptcom',
    version='0.1'
)
