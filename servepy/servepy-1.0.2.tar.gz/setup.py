from distutils.core import setup

setup(
    name="servepy",
    py_modules=['servepy'],
    version="1.0.2",
    author="Stuart Wilcox",
    author_email="stuart_wilcox@outlook.com",
    url="https://github.com/Stuart-Wilcox/servepy",
    description = 'Simple server framework',
    long_description="""
        Servepy is an HTTP server framework modelled after the Express.js library for Node.js
        For more information and for documentation, please visit https://github.com/Stuart-Wilcox/servepy
    """,
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
    ]
)
