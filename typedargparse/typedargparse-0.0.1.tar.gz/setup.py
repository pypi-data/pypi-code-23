from setuptools import setup, find_packages

setup(
    name="typedargparse",
    version="0.0.1",
    description="Simple argparse wrapper with typing",
    url="https://github.com/emakryo/typedargparse",
    author="Ryosuke Kamesawa",
    author_email="emak.ryo@gmail.com",
    licnese="MIT",
    classifier=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities"
    ],
    py_modules=["typedargparse"],
    python_requires='>=3.5'
)
