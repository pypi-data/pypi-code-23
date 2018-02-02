from setuptools import setup

setup(
    name='sl_client',
    version='1.1',
    py_modules=['sl_client'],
    license='BSD 3-Clause',
    description="A Python tool that connects to the Studyportals ServiceLayer using Studyportals reflector and retrieves data.",
    url='https://github.com/studyportals/ServiceLayerClient-python',
    author='Ugne Laima Ciziute',
    author_email='devops@studyportals.com',
    install_requires=['requests'],
	python_requires='>=3'
)