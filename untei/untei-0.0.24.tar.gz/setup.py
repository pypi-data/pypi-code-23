from distutils.core import setup
import os
entry_points = {
    'console_scripts': [
        'untei = untei.static_site_generator:main'
    ]
}

def data_dir(dir_name):
    return [os.path.relpath(os.path.join(root, name), 'untei')
            for root, _, names in os.walk(os.path.join('untei', dir_name))
            for name in names]

datafiles = data_dir('default-themes')
datafiles.extend(data_dir('documentation'))

dependencies = ['parsimonious']
setup(
    name = "untei",
    packages = ["untei"],
    version = "0.0.24",
    description = "Static site generator you can create your own theme by python coding",
    author = "Hara Yuki",
    author_email = "youhui.dev@gmail.com",
    url = "",
    download_url = "",
    keywords = ["static site generator"],
    package_data={ 'untei': datafiles },
    entry_points = entry_points,
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Markup",
        ],
    install_requires = dependencies,
    long_description = """\
Untei is a static site generator. You can configure blog-like websites with markdown documents.
The distictive point of untei from other site generator is that you can create your own theme as if you code in python.
"""
)
