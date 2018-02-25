from setuptools import setup


setup(
    name="conda-list-all-envs",
    version= '0.1',
    author= "Samaksh Goyal",
    author_email="mailsamakshgoyal@gmail.com",
    url="",
    license="BSD",
    description="A tool for validating conda recipes and conda packages",
    packages=['conda_list_all_envs'],
    entry_points='''
        [console_scripts]
        conda-list-all-envs=conda_list_all_envs.cli:cli
        ''',
)

