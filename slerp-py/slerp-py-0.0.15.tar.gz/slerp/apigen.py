import ast
import getpass
import os
import re

from jinja2 import Environment, FileSystemLoader

from .visitor import AnalysisNodeVisitor, ClassVisitor

PATH = os.path.dirname(os.path.abspath(__file__))
# Get the root path
PATH = os.path.abspath(os.path.join(PATH, os.pardir))
print('Path %s', PATH)
TEMPLATE_ENVIRONMENT = Environment(
	autoescape=False,
	loader=FileSystemLoader(os.path.join(PATH, 'templates')),
	trim_blocks=False)


def render_template(template_filename, context):
	return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def get_field_name(fields=None):
	field_names = [];
	for d in fields:
		field_names.append(d['name'])
	return field_names

# noinspection PyTypeChecker
def get_fields(key=None, classes=None):
	for clazz in classes:
		if key in clazz:
			return clazz[key]['fields']
	raise RuntimeError('not found')


def get_class_name(classes=None):
	class_name = []
	for clazz in classes:
		class_name.append([str(x) for x in clazz.keys()])
		pass
	return class_name


def to_snake_case(name):
	s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
	return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def write(file_name=None, content=None):
	f = open(file_name, 'w')
	f.write(content)
	f.close()


def append(file_name=None, content=None):
	f = open(file_name, 'a')
	f.write(content)
	f.close()


def is_function_not_exists(file_name, attrib_name):
	tree = ast.parse(open(file_name, 'r').read(), '')
	visitor = AnalysisNodeVisitor()
	visitor.visit(tree)
	nodes = visitor.functions
	for node in nodes:
		if node.attributes['name'] == attrib_name:
			return False
	return True


def generate_find(domain=None, class_name=None, classes=None, service_file=None, api_file=None, filename=None):
	domain['method_name'] = to_snake_case('Find' + class_name)
	print('You have {}, \nnow please input one of choice in the filter '.format(
		str(get_field_name(domain['fields'])).replace('[', '(').replace(']', ')')))	
	filter_by = input('Filter By : ')
	filter_by_list = []
	service_name = ''
	if ',' in filter_by:
		split = filter_by.split(',')
		for filter_key in split:
			if filter_key.strip() not in get_field_name(domain['fields']):
				print('You are not lucky, your model does not have {}'.format(filter_key.strip()))
				classes[:] = []
				generate(filename)
				return
			else:
				filter_by_list.append(filter_key.strip())
				service_name = domain['method_name'] + '_by_' + '_and_'.join(filter_by_list)
	else:
		if filter_by not in get_field_name(domain['fields']):
			filter_by = ''
		else:
			service_name = domain['method_name'] + '_by_' + filter_by
	domain['filter_by'] = filter_by
	domain['filter_by_list'] = filter_by_list
	if is_function_not_exists(service_file, service_name):
		append(service_file, render_template('service_find.txt', domain))
		append(api_file, render_template('api_find.txt', domain))
		print('Successfully generated module in {}...'.format(service_file))
	else:
		print('You are not lucky, {} has been exist'.format(domain['method_name']))
		print('Lets try again\n')
		classes[:] = []
		generate(filename)


def generate_create(domain=None, class_name=None, classes=None, service_file=None, api_file=None, filename=None):
	domain['method_name'] = to_snake_case('Add' + class_name)
	if is_function_not_exists(service_file, domain['method_name']):
		append(service_file, render_template('service_add.txt', domain))
		append(api_file, render_template('api_add.txt', domain))
		print('Successfully generated module in {}...'.format(service_file))
	else:
		print('You are not lucky, {} has been exist'.format(domain['method_name']))
		classes[:] = []
		generate(filename)


def generate_delete(domain=None, class_name=None, classes=None, service_file=None, api_file=None, filename=None):
	domain['method_name'] = to_snake_case('Delete' + class_name)
	print('You have {}, \nNow select one of all the options you have'.format(
		str(get_field_name(domain['fields'])).replace('[', '(').replace(']', ')')))	
	filter_by = input('Delete By : ')
	filter_by_list = []
	service_name = ''
	if ',' in filter_by:
		split = filter_by.split(',')
		for filter_key in split:
			if filter_key.strip() not in get_field_name(domain['fields']):
				print('You are not lucky, your model does not have {}'.format(filter_key.strip()))
				classes[:] = []
				generate(filename)
				return
			else:
				filter_by_list.append(filter_key.strip())
				service_name = domain['method_name'] + '_by_' + '_and_'.join(filter_by_list)
	else:
		if filter_by not in get_field_name(domain['fields']):
			filter_by = ''
		else:
			service_name = domain['method_name'] + '_by_' + filter_by
	domain['filter_by'] = filter_by
	domain['filter_by_list'] = filter_by_list
	if is_function_not_exists(service_file, service_name):
		append(service_file, render_template('service_delete.txt', domain))
		append(api_file, render_template('api_delete.txt', domain))
		print('Successfully generated module in {}...'.format(service_file))
	else:
		print('You are not lucky, {} has been exist'.format(domain['method_name']))
		print('Lets try again\n')
		classes[:] = []
		generate(filename)


def generate_update(domain=None, class_name=None, classes=None, service_file=None, api_file=None, filename=None):
	domain['method_name'] = to_snake_case('Edit' + class_name)
	print ('You have {}, \nnow please input one of choice in the filter '.format(
		str(get_field_name(domain['fields'])).replace('[', '(').replace(']', ')')))	
	filter_by = input('Update By : ')
	filter_by_list = []
	service_name = ''
	if ',' in filter_by:
		split = filter_by.split(',')
		for filter_key in split:
			if filter_key.strip() not in get_field_name(domain['fields']):
				print('You are not lucky, your model does not have {}'.format(filter_key.strip()))
				classes[:] = []
				generate(filename)
				return
			else:
				filter_by_list.append(filter_key.strip())
				service_name = domain['method_name'] + '_by_' + '_and_'.join(filter_by_list)			
		pass
	else:
		if filter_by not in get_field_name(domain['fields']):
			filter_by = ''
		else:
			service_name = domain['method_name'] + '_by_' + filter_by

	domain['filter_by'] = filter_by
	domain['filter_by_list'] = filter_by_list
	if is_function_not_exists(service_file, service_name):
		append(service_file, render_template('service_update.txt', domain))
		append(api_file, render_template('api_update.txt', domain))
		print('Successfully generated module in {}...'.format(service_file))
	else:
		print('You are not lucky, {} has been exist'.format(service_name))
		print('Lets try again\n')
		classes[:] = []
		generate(filename)


def generate_paging(domain=None, class_name=None, classes=None, service_file=None, api_file=None, filename=None):
	domain['method_name'] = to_snake_case('Get' + class_name)
	print('You have {}, \nNow select one of all the options you have'.format(
		str(get_field_name(domain['fields'])).replace('[', '(').replace(']', ')')))	
	filter_by = input('Filter By :')
	filter_by_list = []
	service_name = ''
	if ',' in filter_by:
		split = filter_by.split(',')
		
		for filter_key in split:
			if filter_key.strip() not in get_field_name(domain['fields']):
				print('You are not lucky, your model does not have {}'.format(filter_key.strip()))
				classes[:] = []
				generate(file)
				return
			else:
				filter_by_list.append(filter_key.strip())
				service_name = domain['method_name'] + '_by_' + '_and_'.join(filter_by_list)
	
	else:
		if filter_by not in get_field_name(domain['fields']):
			print('You are not lucky, your model does not have {}'.format(filter_by))
			classes[:] = []
			generate(filename)
		else:
			service_name = domain['method_name'] + '_by_' + filter_by
	
	order_by = str(input('Order By : ')).strip()	
	domain['order_type'] = 'asc'
	is_asc = input('Is asc order? ')
	if is_asc.lower() == 'yes':
		domain['order_type'] = 'asc()'
	else:
		domain['order_type'] = 'desc()'
	
	if order_by not in get_field_name(domain['fields']):
		print('You are not lucky, your model does not have '.format(order_by))
		print('Lets try again\n')
		classes[:] = []
		generate(filename)
	domain['order_by'] = order_by
	domain['filter_by'] = filter_by
	domain['filter_by_list'] = filter_by_list
	if is_function_not_exists(service_file, service_name):
		append(service_file, render_template('service_pagging.txt', domain))
		append(api_file, render_template('api_pagging.txt', domain))
		print('Successfully generated module in {}...'.format(service_file))
	else:
		print('You are not lucky, {} has been exist'.format(service_name))
		print('Lets try again\n')
		classes[:] = []
		generate(filename)


def generate_all_item(domain=None, class_name=None, classes=None, service_file=None, api_file=None, filename=None):
	domain['method_name'] = to_snake_case('Get' + class_name)
	print('You have {}, \nNow select one of all the options you have'.format(
		str(get_field_name(domain['fields'])).replace('[', '(').replace(']', ')')))	
	filter_by = input('Filter by : ')
	filter_by_list = []
	service_name = ''
	if ',' in filter_by:
		split = filter_by.split(',')
		
		for filter_key in split:
			if filter_key.strip() not in get_field_name(domain['fields']):
				print('You are not lucky, your model does not have {}'.format(filter_key.strip()))
				classes[:] = []
				generate(file)
				return
			else:
				filter_by_list.append(filter_key.strip())
				service_name = domain['method_name'] + '_by_' + '_and_'.join(filter_by_list)
	
	else:
		if filter_by not in get_field_name(domain['fields']):
			print('You are not lucky, your model does not have {}'.format(filter_by))
			classes[:] = []
			generate(filename)
		else:
			service_name = domain['method_name'] + '_by_' + filter_by
	
	
	order_by = str(input('Order by : ')).strip()	
	domain['order_type'] = 'asc'
	is_asc = input('Is this ascending (yes/no) ? ')
	if is_asc.lower() == 'yes':
		domain['order_type'] = 'asc()'
	else:
		domain['order_type'] = 'desc()'
	
	if order_by not in get_field_name(domain['fields']):
		print('You are not lucky, your model does not have '.format(order_by))
		print('Lets try again\n')
		classes[:] = []
		generate(filename)
	domain['order_by'] = order_by
	domain['filter_by'] = filter_by
	domain['filter_by_list'] = filter_by_list
	if is_function_not_exists(service_file, service_name):
		append(service_file, render_template('service_all.txt', domain))
		append(api_file, render_template('api_all.txt', domain))
		print('Successfully generated module in {}...'.format(class_name))
	else:
		print('You are not lucky, {} has been exist'.format(service_name))
		print('Lets try again\n')
		classes[:] = []
		generate(filename)


def generate(filename=None):
	domain = {}
	buf = open(filename, 'r')
	tree = ast.parse(buf.read(), '')
	buf.close()
	visitor = ClassVisitor()
	visitor.visit(tree)
	classes = visitor.get_classes
	print('All right, is this your models file.')
	print ('***************************************************************************** ')
	classes_names = '\n'.join(map(str, [i[0] for i in get_class_name(classes)]))
	print (classes_names)
	print ('***************************************************************************** ')	
	class_name = input('So please select one that you need ? ')		
	q_type = str(input('Okay now, what is query you want to add(c, r, u, or d) ? ')).lower()
	
	domain['class_name_snake'] = to_snake_case(class_name)
	domain['class_name'] = class_name
	service_file = 'service/{}_service.py'.format(domain['class_name_snake'])
	api_file = 'api/{}_api.py'.format(domain['class_name_snake'])
	if not os.path.isdir('service'):
		os.makedirs('service')
		write(service_file, render_template('service_base.txt', domain))
		write('service/__init__.py', '')
	else:
		if not os.path.isfile(service_file):
			write(service_file, render_template('service_base.txt', domain))
	
	if not os.path.isdir('api'):
		os.makedirs('api')
		write(api_file, render_template('api_base.txt', domain))
		write('api/__init__.py', '')
	else:
		if not os.path.isfile(api_file):
			write(api_file, render_template('api_base.txt', domain))
	domain['fields'] = get_fields(key=class_name, classes=classes)
	if q_type == 'c':
		generate_create(domain=domain, class_name=class_name, classes=classes, service_file=service_file,
		                api_file=api_file,
		                filename=filename)
	elif q_type == 'u':
		generate_update(domain=domain, class_name=class_name, classes=classes, service_file=service_file,
		                api_file=api_file,
		                filename=filename)
	elif q_type == 'r':		
		is_paging = str(input('Do you want pagination (yes/no) ? ')).lower()
		paging = True if is_paging == 'yes' else False
		if paging:
			generate_paging(domain=domain, class_name=class_name, classes=classes, service_file=service_file,
			                api_file=api_file,
			                filename=filename)
			return		
		is_one_item = str(input('is this just one item (yes/no) ?')).lower()
		one_item = True if is_one_item == 'yes' else False
		if one_item:
			generate_find(domain=domain, class_name=class_name, classes=classes, service_file=service_file,
			              api_file=api_file,
			              filename=filename)
			return
		
		is_all_item = str(input('is have all item (yes/no) ?')).lower()
		
		all_item = True if is_all_item == 'yes' else False
		
		if all_item:
			generate_all_item(domain=domain, class_name=class_name, classes=classes, service_file=service_file,
			                  api_file=api_file,
			                  filename=filename)
		else:
			print('sorry i dont know what you want, bye...')
			exit(0)
	elif q_type == 'd':
		generate_delete(domain=domain, class_name=class_name, classes=classes, service_file=service_file,
		                api_file=api_file,
		                filename=filename)
	else:
		print('You are not lucky, please choose correctly')
		generate(filename)


def main():
	print('\n\nHello {}, my name is Typo.\n'
	      'i can help you to create flask api code\nbut you need to answer my question first.'.format(
		getpass.getuser()))
	print('***************************************************************************** ')	
	file_name = str(input('Where is your model file ? '))
	if not os.path.isfile(file_name):
		print('Invalid file path, try again.')		
		file_name = str(input('Where is your model file ? '))
		generate(file_name)
	else:
		generate(file_name)

if __name__ == '__main__':
	main()