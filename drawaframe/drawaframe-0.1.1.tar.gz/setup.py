from setuptools import setup

setup(  
    name="drawaframe",
    version='0.1.1',
    description="A simple way to generate decorative frames for CLI applications.",
    long_description="A simple way to generate decorative frames for CLI applications.Create shapes and borders with just a few lines of code",
    author="Jagadeesh Kotra",
    author_email="hello@jagadeesh.me",
    url="https://github.com/jagadeesh-kotra/drawaframe",
    license="Apache",
    py_modules=['drawaframe'],
    entry_points='''
        [console_scripts]
        drawaframe=drawaframe:main
    '''
)
