from setuptools import setup, find_packages

try:
    with open('README.rst') as file:
        long_description = file.read()
except Exception as error:
    print("Could not find README.rst for long description. Error: {}".format(
        error))
    print("Leaving long_description as None")
    long_description = None

setup(
    name='quoteBot',
    author='elias julian marko garcia',
    author_email='elias.jm.garcia@gmail.com',
    description='a package to create text quote bots on twitter quickly',
    url='https://github.com/ejmg/quoteBot',
    version='0.2.52dev',
    packages=find_packages(),
    entry_points={
        "console_scripts": ['quoteBot = quoteBot.quoteBot:cli'],
    },
    install_requires=['nltk', 'tweepy', 'click'],
    license='MIT',
    long_description=long_description)
