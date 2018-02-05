from setuptools import find_packages, setup
import os

version = "1.0.0"

readme = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
requirements = [i.strip() for i in open(req_file).readlines()]

setup_params = dict(
    name="pymongosl",
    version=version,
    description="MongoDB DBAPI Driver",
    author="YangSheBing",
    author_email="811068990@qq.com",
    long_description=readme,
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Database :: Front-Ends',
    ],
    keywords='MongoDB SQLAlchemy',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "sqlalchemy.dialects":
            ["mongodb = pymongosl.dialect:MongoDBDialect"]
    },
    install_requires=requirements
)

if __name__ == '__main__':
    setup(**setup_params)
