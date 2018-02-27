from distutils.core import setup

setup(
    name='CloeePy',
    version='0.0.0',
    packages=['cloeepy',],
    package_data = {
        'cloeepy': ['data/*.yml'],
    },
    include_package_data=True,    # include everything in source control
    license='MIT',
    description="Light weight framework for non-HTTP systems.",
    long_description=open('README.md').read(),
    install_requires=[
          "pyaml>=17",
          "python-json-logger>=0.1",
          "PyYAML>=3,<4",
     ],
     url = "https://github.com/cloeeai/CloeePy",
     author = "Scott Crespo",
     author_email = "sccrespo@gmail.com",
     keywords = "mini framework yaml cloee",
     python_requires='~=3.3',
)
