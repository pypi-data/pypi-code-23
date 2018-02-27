from distutils.core import setup

setup(
    name='CloeePy-Redis',
    version='0.0.0-rc1',
    packages=['cloeepy_redis',],
    package_data = {
        'cloeepy_redis': ['data/*.yml'],
    },
    license='MIT',
    description="Plugin for CloeePy Framework",
    long_description=open('README.md').read(),
    install_requires=[
        "redis>=2,<3",
        "CloeePy>=0",
     ],
     url = "https://github.com/cloeeai/CloeePy-Redis",
     author = "Scott Crespo",
     author_email = "sccrespo@gmail.com",
     keywords = "mini framework cloee cloeepy redis",
     python_requires='~=3.3',
)
