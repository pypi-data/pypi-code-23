from setuptools import setup

setup(
    name = "fazlamesai",
    py_modules = ["fazlamesai"],
    version = "0.1.0",
    description = "A client library for the fazlamesai.net API",
    author = "Gokberk Yaltirakli",
    author_email = "webdosusb@gmail.com",
    url = "https://github.com/gkbrk/fazlamesai-py",
    keywords = ["fazlamesai", "api", "client"],
    install_requires = ["requests"]
)
