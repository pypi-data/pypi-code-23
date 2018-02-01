from setuptools import setup

setup(name="cvbankas_scraper",
      version="0.0.2",
      description="cvbankas.lt web site scraper",
      url="https://github.com/tomasrasymas/cvbankas_scraper",
      author="Tomas Rasymas",
      author_email="tomas.rasymas@gmail.com",
      license="MIT",
      entry_points={
        "console_scripts": ["cvbankas_scraper=cvbankas_scraper.command_line:main"],
      },
      data_files = [("", ["LICENSE"])],
      install_requires=[
          "requests==2.18.4",
          "beautifulsoup4==4.6.0"
      ],
      packages=["cvbankas_scraper"])