from setuptools import setup, find_packages

try:
    from pypandoc import convert
    def read_markdown(file: str) -> str:
        return convert(file, "rst")
except ImportError:
    def read_markdown(file: str) -> str:
        return open(file, "r").read()

setup(
    name="temphelpers",
    version="1.0.0",
    author="Colin Nolan",
    author_email="colin.nolan@sanger.ac.uk",
    packages=find_packages(exclude=["tests"]),
    url="https://github.com/wtsi-hgi/python-temp-helpers",
    license="MIT",
    description="Python library to help with using temp files and directories",
    long_description=read_markdown("README.md"),
    test_suite="temphelpers.tests",
    zip_safe=True
)
