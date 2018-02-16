from setuptools import setup
 
setup(
    name = 'gsvloader',
    packages = ['gsvloader'],
 #   install_requires=['shapely','tqdm', 'overpass', 'shapely', 'numpy', 'urllib3', 'Pillow'],
    version = '0.1.5',
    description = 'Google Street View Retrieval',
    author='Poom Wettayakorn',
    author_email='poom.wettayakorn@gmail.com',
    url='https://github.com/pcrete',
    classifiers=[]
)

# python setup.py sdist && twine upload dist/gsvloader-0.1.4.tar.gz && sudo pip3 install --upgrade gsvloader