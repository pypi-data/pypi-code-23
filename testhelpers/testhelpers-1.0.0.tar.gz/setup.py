from setuptools import setup, find_packages

try:
    from pypandoc import convert
    def read_markdown(file: str) -> str:
        return convert(file, "rst")
except ImportError:
    def read_markdown(file: str) -> str:
        return open(file, "r").read()

setup(
    name="testhelpers",
    version="1.0.0",
    author="Colin Nolan",
    author_email="colin.nolan@sanger.ac.uk",
    packages=find_packages(exclude=["tests"]),
    url="https://github.com/wtsi-hgi/python-test-helpers",
    license="MIT",
    description="Python library to help with creating tests",
    long_description=read_markdown("README.md"),
    test_suite="testhelpers.tests",
    zip_safe=True
)
