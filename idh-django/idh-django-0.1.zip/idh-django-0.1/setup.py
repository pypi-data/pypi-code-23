from distutils.core import setup
setup(
    name = 'idh-django',
    packages = [
        'idh.django.core.basic',
        'idh.django.core.cache',
        'idh.django.core.formatter',
        'idh.django.core',
        'idh.django',
        'idh',
    ],
    version = '0.1',
    description = 'Ideahut Django Library',
    author = 'Thomson470',
    author_email = 'thomson470@gmail.com',
    license='MIT',
    #url = 'https://github.com/peterldowns/mypackage',
    #download_url = 'https://github.com/peterldowns/mypackage/archive/0.1.tar.gz',
    keywords = ['django', 'basic', 'api'],
    #classifiers = [],
    install_requires=['dicttoxml>=1.7.4', 'dj-static>=0.0.6', 'django>=2.0.1', 'django-dotenv>=1.4.2', 'redis>=2.10.6', 'static3>=0.7.0']
    #install_requires=['dicttoxml', 'dj-static', 'django', 'django-dotenv', 'redis', 'static3'],
)