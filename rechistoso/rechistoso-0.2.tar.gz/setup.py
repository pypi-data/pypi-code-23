from setuptools import setup, find_packages

setup(
    name="rechistoso",
    version="0.2",
    description="Un chiste rechistoso",
    entry_points={
        'console_scripts': ['rechistoso=rechistoso.cli:main']
    },
    author="Luciano Serruya Aloisi",
    author_email="lucianoserruya@gmail.com",
    license="MIT",
    packages=find_packages()
)
