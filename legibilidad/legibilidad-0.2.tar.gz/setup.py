from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='legibilidad',
      version='0.2',
      description='Spanish text readability calculation',
      long_description=readme(),
      url='https://gitlab.com/__alexander__/legibilidad',
      author='Alexander Ayasca',
      author_email='alexander.ayasca.esquives@gmail.com',
      license='MIT',
      packages=['legibilidad'],
      zip_safe=False)
