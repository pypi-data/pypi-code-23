from setuptools import setup

setup(
    name='BCPorter',
    version='1.0.0',
    packages=[''],
    url='',
    license='',
    description='',
    install_requires=['pywin32', "pillow", "docxtpl"],
    py_modules=['bcporter'],
    entry_points={
        "console_scripts": ["bcporter=bcporter:command_line_tool"]
    },
)
