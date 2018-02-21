from setuptools import setup


def readme():
    with open("README.rst") as f:
        return f.read()


exec(open('topos/version.py', 'r').read())


setup(name='topos',
      version=__version__,
      description="Mesh generation with a blend of python and maths",
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Multimedia :: Graphics'
      ],
      author='Alex Carney',
      author_email="alcarneyme@gmail.com",
      license='MIT',
      packages=['topos'],
      install_requires=[
          'numpy'
      ],
      setup_requires=['pytest-runner'],
      test_suite='tests',
      tests_require=['pytest', 'hypothesis'],
      python_requires='>=3.0',
      include_package_data=True,
      zip_safe=False)
