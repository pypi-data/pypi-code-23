from setuptools import setup

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(
        name='bluedb',
        author='EnderDas',
        url='https://github.com/Enderdas/BlueDB',
        packages=['BlueDB'],
        version='0.2.4',
        description='Like shelves but better...',
        long_description=readme
    )
