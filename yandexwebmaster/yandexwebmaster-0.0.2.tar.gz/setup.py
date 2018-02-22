import os
from setuptools import setup, find_packages

# try:
#     import pypandoc
#     long_description = pypandoc.convert('README.md', 'rst', format='markdown_github', extra_args=("--no-wrap",))
# except:
#     long_description = ''

import pypandoc
long_description = pypandoc.convert('README.md', 'rst', format='markdown_github', extra_args=("--wrap=none",))

import yandexwebmaster
version = yandexwebmaster.__version__

setup(
    name = 'yandexwebmaster',
    version = version,
    description = 'YandexWebmaster API',
    long_description=long_description,
    author = 'Danillab',
    author_email = 'danillab@yandex.ru',
    install_requires = [
        'requests',
    ],
    packages = find_packages(exclude=['test', "*.egg-info"]),
    license = "MIT",
    keywords='yandex webmaster',
)