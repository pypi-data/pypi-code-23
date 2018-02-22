from setuptools import setup, find_packages

setup(
    name='spot-memair',
    version='2018.2.22.0',
    description='updates memair with spot data',
    long_description=open('README.rst').read(),
    url='https://github.com/gregology/spot-memair',
    author='Greg Clarke',
    author_email='greg@gho.st',
    license='MIT',
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python'
    ],
    keywords='spot memair location',
    packages=find_packages(),
    package_data={
      'spot_memair': []
    }
)
