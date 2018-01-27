from setuptools import setup

setup(
	name = 'modelo-visao',
	version = '1.1',
	description = 'Projeto traz bibliotecas do Modelo e VisaoHTML para o appLojas',
	url = 'https://github.com/plimo263',
	author = 'Marcos Felipe da Silva Jardim',
	author_email = 'plimo263@gmail.com',
	license = 'MIT',
	classifiers = [
		# Informa em qual versao do python meu projeto trabalha
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.2',
    	'Programming Language :: Python :: 3.3',
    	'Programming Language :: Python :: 3.4',
    	'Programming Language :: Python :: 3.5',
    	'Programming Language :: Python :: 3.6',
	],
	python_requires = '>=3',
	install_requires = ['pymssql', 'pymysql'],
	py_modules = ['Modelo','VisaoHTML'],
);

