from setuptools import setup, find_packages

setup(name='NCP_ELSA',
      description="""This is for ELSA(Effective Log Search & Analytics) service of NAVER Cloud Platform""",
      version='0.14',
      url='https://github.com/ultimatelife/NCP_ELSA_PYTHON',
      author='geonwoo.kim',
      keywords=['NCP', 'clova', 'ELSA', 'NCP_ELSA', 'elsa'],
      author_email='drama0708@gmail.com',
      license='Naver Cloud Platform',
      python_requires='>=3.6',
      classifiers=[
          'Programming Language :: Python :: 3.6'
      ],
      packages=find_packages(),
      install_requires=[
          'requests>=2.17.3'
      ]
      )
