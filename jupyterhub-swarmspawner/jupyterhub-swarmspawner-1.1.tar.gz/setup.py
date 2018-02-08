from setuptools import setup

setup(
    name='jupyterhub-swarmspawner',
    version='1.1',
    description='SwarmSpawner: A spawner for JupyterHub that uses Docker Swarm s services',
    url='https://github.com/wakonp/SwarmSpawner/',
    author='Philipp Wakonigg',
    author_email='philipp.wakonigg@edu.fh-joanneum.at',
    license='BSD',
    packages=['wakonpspawner'],
    install_requires=[
        'docker',
        'jupyterhub',
    ]
)
