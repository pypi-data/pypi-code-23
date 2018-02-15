from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name="rechistoso",
    version="0.2.1",
    description="Un chiste rechistoso",
    long_description=readme(),
    packages=find_packages(),
    entry_points={
        'console_scripts': ['rechistoso=rechistoso.cli:main']
    },
    author="Luciano Serruya Aloisi",
    author_email="lucianoserruya@gmail.com",
    license="MIT",
    keywords="chiste gracioso muybueno bueno funny joke good really funniest",
)
