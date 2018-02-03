from setuptools import setup

setup(
    name='pyxeoma',
    packages=['pyxeoma'],
    version='1.3',
    description='Python wrapper for Xeoma web server API',
    author='Jerad Meisner',
    author_email='jerad.meisner@gmail.com',
    url='https://github.com/jeradM/pyxeoma',
    download_url='https://github.com/jeradM/pyxeoma/archive/1.3.tar.gz',
    keywords=['Xeoma'],
    install_requires=[
        'aiohttp'
    ],
    classifiers=[]
)
