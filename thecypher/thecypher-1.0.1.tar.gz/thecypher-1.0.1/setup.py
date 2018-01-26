from setuptools import setup

setup(
    name='thecypher',
    version='1.0.01',
    description='Retrieve Music Lyrics',
    author='Timothy James Dobbins',
    author_email='tmthyjames@gmail.com',
    url='https://github.com/tmthyjames/cypher',
    install_requires=['requests', 'beautifulsoup4'],
    scripts=['thecypher'] 
)
