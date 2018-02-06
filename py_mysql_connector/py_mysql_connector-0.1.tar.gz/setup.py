# *** IMPORTS *** #
from distutils.core import setup

# *** SETUP *** #
setup(
    name = 'py_mysql_connector',
    packages = ['py_mysql_connector'],
    version = '0.1',
    description = 'MySQL database connector',
    author = 'Alejandro Carmona Mejia',
    author_email = 'alejandro.carmonamejia@gmail.com',
    url = 'https://github.com/alexkar7/py_mysql_connector',
    keywords = ['db', 'mysql', 'connector'], 
    install_requires=[
          'mysql-connector-python',
    ],
    classifiers = [],
)
