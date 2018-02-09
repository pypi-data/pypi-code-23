from setuptools import setup

setup(name='vsionailibs',
      version='1.0.1',
      description='the public libs of vsion.ai',
      url='https://git.tech.rz.db.de/ZhenyuGeng/vsion-ai-libs.git',
      author='Zhenyu Geng',
      author_email='zhenyu.geng@deutschebahn.com',
      license='MIT',
      packages=['vsionailibs'],
      install_requires=[
            'botocore',
            'boto3',
            'numpy',
            'opencv-python'
      ],
      zip_safe=False)
