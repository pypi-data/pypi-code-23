from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), "r") as f:
    long_description = f.read()

setup(name='resource_container',
      version='1.1',
      description='A utility for managing Door43 Resource Containers',
      long_description=long_description,
      url='https://github.com/unfoldingWord-dev/python-resource-container',
      author='unfoldingWord',
      author_email='joel@neutrinographics.com',
      license='MIT',
      classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
      ],
      packages=find_packages(),
      keywords=["rc", "resource container", "client"],
      install_requires=[
            'pyyaml',
            'uw_tools'
      ],
      test_suite="tests",
      zip_safe=False
)
