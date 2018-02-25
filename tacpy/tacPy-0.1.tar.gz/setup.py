from setuptools import setup

version = '0.1'

setup(
    name='tacPy',
    version=version,
    packages=['tacPy'],
    url='https://github.com/jgillmanjr/tacPy',
    license='',
    author='Jason Gillman Jr.',
    author_email='jason@rrfaae.com',
    description='A library for working with the Talend Administration Center API',
    install_requires=['requests'],
    package_data={
        'tacPy': ['full_tac_api_help.txt.example']
    }
)
