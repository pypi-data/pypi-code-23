from setuptools import setup, find_packages

setup(
    name='findiffpy',
    version='1.0.0',
    keywords=('finite difference method', 'elliptic equation'),
    description='Using steepest decent, conjugate gradient and preconditioned conjugate decent to solve finite '
                'difference method for elliptic equations',
    license='MIT License',

    author='Davion',
    author_email='findiffpy@gmail.com',
    include_package_data=True,
    packages=find_packages(),
    platforms='any',
    install_requires=[],
)
