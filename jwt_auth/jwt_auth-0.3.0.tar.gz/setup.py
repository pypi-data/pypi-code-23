from setuptools import setup

setup(name='jwt_auth',
      version='0.3.0',
      description='The JWT AUTH API',
      url='https://github.com/CoinLQ/jwt_auth',
      author='Xiandian',
      author_email='lvpython@gmail.com',
      license='MIT',
      packages=['jwt_auth', 'jwt_auth.migrations', 'jwt_auth.tests'],
      #download_url = 'https://github.com/CoinLQ/jwt_auth/archive/master.zip',
      install_requires=[
            'djangorestframework-jwt==1.11.0',
            'djangorestframework==3.7.3',
      ],
      zip_safe=True)
