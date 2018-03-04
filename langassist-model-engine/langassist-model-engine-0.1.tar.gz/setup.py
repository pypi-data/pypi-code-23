from setuptools import find_packages, setup

setup(
    name="langassist-model-engine",
    version="0.1",
    url="https://langassist.rorybyrne.me",
    description="For building and maintaining the ML models in LangAssist",
    author="Rory Byrne",
    author_email="rory.byrne57@mail.dcu.ie",
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=['pandas',
                      'nltk',
                      'sklearn',
                      'numpy',
                      'scipy',
                      'boto3',
                      's3io']
)