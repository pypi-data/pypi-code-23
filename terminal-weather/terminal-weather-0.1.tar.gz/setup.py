from setuptools import setup
 
setup (
    name='terminal-weather',
    description='terminal weather script',
    version='0.1',
    scripts=['src/weather.py', 'src/colors.py'],
    packages=["src"]
    )
