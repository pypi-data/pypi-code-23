from distutils.core import setup

entry_points = {
    'console_scripts': [
        'untei = untei.static_site_generator:main'
    ]
}
setup(
    name = "untei",
    packages = ["untei"],
    version = "0.0.2",
    description = "Static site generator you can create your own theme by python coding",
    author = "Hara Yuki",
    author_email = "youhui.dev@gmail.com",
    url = "",
    download_url = "",
    keywords = ["static site generator"],
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
    long_description = """\
Untei is a static site generator. You can configure blog-like websites with markdown documents.
The distictive point of untei from other site generator is that you can create your own theme as if you code in python.
"""
)
