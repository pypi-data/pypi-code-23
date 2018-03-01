from setuptools import setup, find_packages

setup(
    name="ava-sdk",
    version="0.1.0",
    description="AVA Python SDK",
    url="http://www.qiniu.com",
    maintainer="Qiniu ATLab",
    maintainer_email="ai@qiniu.com",
    packages=find_packages(),
    install_requires=[
        "scikit-learn==0.19.1",
        "requests==2.18.1",
        "qiniu==7.1.4",
        "rfc3339==5.2",
        "tornado==4.5.1",
        "opencv-python==3.4.0.12",
        "mxnet==0.10.0.post2",
        "Pillow==4.2.1",
        "numpy==1.14.0",
    ],
)
