from distutils.core import setup

setup(
    name='CloeePy-Mongo',
    version='0.0.0-rc1',
    packages=['cloeepy_mongo',],
    package_data = {
        'cloeepy': ['data/*.yml'],
    },
    license='MIT',
    description="MongoDB Plugin for CloeePy Framework",
    long_description=open('README.md').read(),
    install_requires=[
        "pymongo>=3.0,<4",
        "CloeePy>=0.0",
     ],
     url = "https://github.com/cloeeai/CloeePy-Mongo",
     author = "Scott Crespo",
     author_email = "sccrespo@gmail.com",
     keywords = "mini framework cloee cloeepy mongo mongodb",
     python_requires='~=3.3',
)
