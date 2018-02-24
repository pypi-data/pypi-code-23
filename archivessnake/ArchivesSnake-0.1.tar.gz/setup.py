from setuptools import setup, find_packages

setup(
    name="ArchivesSnake",
    url="https://github.com/archivesspace-labs/ArchivesSnake",
    author="ArchivesSnake Developer Group",
    author_email="asnake.developers@gmail.com", 
    version="0.1",
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
    ],
    install_requires=[
        "attrs",
        "boltons",
        "pyyaml",
        "requests",
	"structlog",
    ],
)
