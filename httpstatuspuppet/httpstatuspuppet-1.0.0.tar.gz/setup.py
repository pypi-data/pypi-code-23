from setuptools import setup, find_packages

try:
    from pypandoc import convert
    def read_markdown(file: str) -> str:
        return convert(file, "rst")
except ImportError:
    def read_markdown(file: str) -> str:
        return open(file, "r").read()

setup(
    name="httpstatuspuppet",
    version="1.0.0",
    packages=find_packages(exclude=["tests"]),
    install_requires=open("requirements.txt", "r").readlines(),
    url="https://github.com/wtsi-hgi/http-status-puppet.git",
    license="MIT",
    description="A HTTP server that will return a status code of your choice",
    long_description=read_markdown("README.md"),
    zip_safe=True
)
