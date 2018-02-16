from setuptools import setup
 
setup(
    name = 'gsvloader',
    packages = ['gsvloader'],
    install_requires=['shapely','tqdm', 'overpass', 'shapely', 'numpy', 'urllib3', 'Pillow'],
    version = '0.1.4',
    description = 'Google Street View Retrieval',
    author='Poom Wettayakorn',
    author_email='poom.wettayakorn@gmail.com',
    url='https://github.com/pcrete',
    classifiers=[]
)
