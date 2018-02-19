from setuptools import setup, find_packages

setup(name='dataClay',
      version='0.7.3',
      install_requires=["enum34",
                        "pyyaml",
                        "lru-dict",
                        "Jinja2",
                        "PyYAML",
                        "decorator",
                        "grpcio>=1.7.0",
                        "grpcio-tools>=1.7.0",
                        "protobuf",
                        "psutil"
                        ],
      description='Python library for dataClay',
      packages=find_packages("src"),
      package_dir={'':'src'},
      package_data={
        # All .properties files are valuable "package data"
        '': ['*.properties'],
      },
      )
