from setuptools import setup

setup(
    name='pytotp',
    version=3,
    description=(
        'one time password (totp) for python. c2fa'
    ),
    author='cevin',
    author_email='cevin.cheung@gmail.com',
    license='BSD License',
    packages=["pytotp"],
    platforms=["all"],
    url='https://github.com/cevin/pytotp',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)