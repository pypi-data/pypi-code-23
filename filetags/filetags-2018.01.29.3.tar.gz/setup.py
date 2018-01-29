from distutils.core import setup

setup(
    name="filetags",
    version="2018.01.29.3",
    description="Management of simple tags within file names",
    author="Karl Voit",
    author_email="tools@Karl-Voit.at",
    url="https://github.com/novoid/filetags",
    download_url="https://github.com/novoid/filetags/zipball/master",
    keywords=["tagging", "tags", "file managing", "file management", "files", "tagtrees", "tagstore", "tag-based navigation", "tag-based filter"],
    install_requires=["colorama", "pyreadline", "clint"],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        ],
    long_description="""\
filetags
-----------------------------
This Python script adds, removes, and manages tags in file names as in following examples:

    file without time stamp in name -- tag2.txt

    file name with several tags -- tag1 tag2.jpeg

    another example file name with multiple example tags -- fun videos kids.mpeg

    2013-05-09 a file name with ISO date stamp in name -- tag1.jpg

    2013-05-09T16.17 file name with time stamp -- tag3.csv

There are many more cool features provided by this tool.
Please read https://github.com/novoid/filetags/ for further information and descriptions.
"""
)
