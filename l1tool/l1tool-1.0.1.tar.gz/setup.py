from setuptools import setup, find_packages

with open("requirments.txt", 'r') as f:
    required = f.read().splitlines()

setup(
    name="l1tool",
    version="1.0.1",
    description="L1 Regularizer for GNSS Time series change and offsets detection.",
    license="GPL v3",
    author="WU Dingcheng",
    url="https://github.com/wudingcheng/l1tool",
    packages=find_packages(),
    install_requires=required,
    entry_points={"console_scripts": ["l1tool=l1tool:main"]}

)
