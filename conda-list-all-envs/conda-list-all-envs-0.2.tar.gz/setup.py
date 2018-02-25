from setuptools import setup


setup(
    name="conda-list-all-envs",
    version= '0.2',
    author= "Samaksh Goyal",
    author_email="mailsamakshgoyal@gmail.com",
    url="",
    license="BSD",
    description="A tool for finding all of the packages inside all enviornments",
    packages=['conda_list_all_envs'],
    entry_points='''
        [console_scripts]
        conda-list-all-envs=conda_list_all_envs.cli:cli
        ''',
)

