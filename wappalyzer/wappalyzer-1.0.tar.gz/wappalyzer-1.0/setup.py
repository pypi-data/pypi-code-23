from setuptools import setup

setup(name="wappalyzer",
      version="1.0",
      description="A python implementation of wappalyzer",
      url="https://www.github.com/shaddygarg/framework-identifier",
      license='MIT',
      author="Shaddy Garg",
      author_email='shaddygarg1@gmail.com',
      package=['wappalyze'],
      install_requires=[
                        'requests',
                        'bs4',
                        ],
      entry_points={
                    'console_scripts': [
                                      'wappalyze = wappalyze.wappalyze:main'
                                                ],
                    })

