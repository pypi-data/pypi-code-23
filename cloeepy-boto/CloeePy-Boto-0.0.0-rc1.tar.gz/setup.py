from distutils.core import setup

setup(
    name='CloeePy-Boto',
    version='0.0.0-rc1',
    packages=['cloeepy_boto',],
    package_data = {
        'cloeepy_boto': ['data/*.yml'],
    },
    license='MIT',
    description="Boto Plugin for CloeePy Framework",
    long_description=open('README.md').read(),
    install_requires=[
        "boto3>=1,<2",
        "CloeePy>=0",
     ],
     url = "https://github.com/cloeeai/CloeePy-Boto",
     author = "Scott Crespo",
     author_email = "sccrespo@gmail.com",
     keywords = "mini framework cloee cloeepy boto boto3",
     python_requires='~=3.3',
)
