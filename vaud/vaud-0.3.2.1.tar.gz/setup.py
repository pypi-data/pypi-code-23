
from setuptools import setup
from vaud import __version__
from os.path import isfile

_readme = 'README.rst'
long_description = ''
if isfile(_readme):
    with open(_readme) as f:
        long_description = f.read()


requires = []

setup(
    name='vaud',
    version=__version__,
    description='Simple vk.com audio address decoder',
    long_description=long_description,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        ],
    keywords=['vk.com audio address decoder', 'vk music'],
    author="Zharkov Sergey",
    author_email="sttvpc@gmail.com",
    url="https://github.com/yuru-yuri/vk-audio-url-decoder/",
    download_url='https://github.com/yuru-yuri/vk-audio-url-decoder/archive/' + __version__ + '.tar.gz',
    license="MIT",
    packages=['vaud'],
    include_package_data=False,
    zip_safe=False,
    tests_require=requires,
    install_requires=requires,
    test_suite="tests",
)
