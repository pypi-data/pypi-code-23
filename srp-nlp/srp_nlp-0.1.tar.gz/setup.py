from setuptools import setup

setup(name='srp_nlp',
      version='0.1',
      description='Reusable NLP stuff in Python',
      url='https://github.com/jwilber/srp_nlp',
      author='Jared Wilber',
      author_email='jdwlbr@gmail.com',
      license='GNU3',
      packages=['srp_nlp'],
      install_requires=[
            'numpy',
            'gensim',
            'nltk'
      ],
      zip_safe=False)