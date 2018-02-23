import pypandoc

description = pypandoc.convert('README.md', 'rst')
description = description.replace("\r", "")  # YOU  NEED THIS LINE

with open("README.rst", "w") as text_file:
    text_file.write(description)
