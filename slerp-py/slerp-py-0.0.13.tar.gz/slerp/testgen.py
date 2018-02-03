from visitor import AnalysisNodeVisitor
from slerp import is_json, to_camel_case
from apigen import render_template, append, write
import ast
import json
import os

def main():
	file_path = raw_input('Where is your api file? ')
	buf = open(file_path, 'r')
	file_name = os.path.basename(file_path)
	file_name = file_name.replace('_api.py', '')
	class_name = 'Test'+to_camel_case(file_name)
	service_file = 'test_' + file_name + '.py'
	if not os.path.isdir('tests'):
		os.makedirs('tests')
		write('tests/'+service_file, render_template('test_base.txt', {'class_name': class_name}))
		write('tests/__init__.py', '')
	else:
		if not os.path.isfile(service_file):
			write('tests/'+ service_file, render_template('test_base.txt', {'class_name': class_name}))
	tree = ast.parse(buf.read())
	buf.close()
	visitor = AnalysisNodeVisitor()
	visitor.visit(tree)
	
	for func in visitor.functions:
		docstring = func.attributes['docstring']
		if not is_json(docstring):
			continue
		doc_json = json.loads(docstring, encoding='UTF-8')
		func.attributes['docstring'] = doc_json
		append('tests/'+service_file,render_template('test_api.txt', func.attributes))
	pass


if __name__ == '__main__':
	# /home/kiditz/slerp-rest-api/app/api/learning_material_api.py
	main()