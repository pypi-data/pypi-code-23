from setuptools import setup, find_packages

setup(name='NCP_CSS',
      description="""This is for CSS(Clova Speech Synthesis) service of NAVER Cloud Platform\thttps://github.com/ultimatelife/NCP_CSS""",
      version='0.14',
      url='https://github.com/ultimatelife/NCP_CSS.git',
      author='geonwoo.kim',
      keywords=['NCP', 'Papago', 'Clova', 'clova', 'CSS'],
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
