from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='shadowhack',
      version='0.1',
      description='The ShadowHack',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='shadowhack',
      url='http://github.com/gitrahul9/shadowhack',
      author='shadowhack',
      author_email='rahulsingal2009@gmail.com',
      license='MIT',
      packages=['shadowhack'],
      include_package_data=True,
      zip_safe=False)
