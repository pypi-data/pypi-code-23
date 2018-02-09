import ast
import os


def _get_last_line_number(nodes):
	children = None
	if hasattr(nodes[-1], 'orelse'):
		children = nodes[-1].orelse
	elif hasattr(nodes[-1], 'finalbody'):
		children = nodes[-1].finalbody
	elif hasattr(nodes[-1], 'body'):
		children = nodes[-1].body
	if children:
		return max(nodes[-1].lineno, _get_last_line_number(children))
	else:
		return nodes[-1].lineno


class Node(object):
	
	def __init__(self, attributes={}, parent=None):
		self.__dict__.update({'_children': [], '_parent': None, '_attributes': attributes})
		self.parent = parent
	
	def __repr__(self):
		return self.__class__.__name__ + "(attributes = " + str(self.attributes) + ")"
	
	@property
	def attributes(self):
		return self._attributes
	
	@attributes.setter
	def attributes(self, attributes):
		self._attributes = attributes
	
	@property
	def parent(self):
		return self._parent
	
	@parent.setter
	def parent(self, parent):
		if self._parent != None:
			self._parent.removeChild(self)
		self._parent = parent
		if self._parent != None:
			self._parent.addChild(self)
	
	@property
	def children(self):
		return self._children
	
	def removeChild(self, child):
		if child in self.children():
			del self._children[self._children.indexof(child)]
	
	def addChild(self, child):
		if not child in self._children:
			self._children.append(child)


class AnalysisNodeVisitor(ast.NodeVisitor):
	
	def __init__(self, rootNode=None):
		self._modules = []
		self._classes = []
		self._functions = []
		self._variables = []
		self._imports = []
		self._rootNode = rootNode
		self._parentNode = rootNode
		self._level = 0
	
	@property
	def rootNode(self):
		return self._rootNode
	
	@property
	def imports(self):
		return self._imports
	
	@property
	def functions(self):
		return self._functions
	
	@property
	def variables(self):
		return self._variables
	
	@property
	def classes(self):
		return self._classes
	
	def visit_Import(self, node):
		for name in node.names:
			importNode = Node(attributes={'type': 'import', 'names': map(lambda x: x.name, node.names)},
			                  parent=self._parentNode)
			self._imports.append(importNode)
		ast.NodeVisitor.generic_visit(self, node)
	
	def visit_ImportFrom(self, node):
		for name in node.names:
			importNode = Node(attributes={'line_number': node.lineno, 'type': 'from_import', 'module': node.module,
			                              'names': map(lambda x: x.name, node.names)}, parent=self._parentNode)
			self._imports.append(importNode)
		ast.NodeVisitor.generic_visit(self, node)
	
	def visit_Assign(self, node):
		for target in node.targets:
			self._add_target_to_variables(target)
		ast.NodeVisitor.generic_visit(self, node)
	
	def visit_AssignAug(self, node):
		self._add_target_to_variables(node.target)
		ast.NodeVisitor.generic_visit(self, node)
	
	def _add_target_to_variables(self, target):
		if hasattr(target, 'value'):
			self._add_target_to_variables(target.value)
		elif hasattr(target, 'id'):
			if not target.id in self._variables and not target.id == "self":
				variableNode = Node(attributes={'type': 'variable', 'name': target.id}, parent=self._parentNode)
				self._variables.append(variableNode)
	
	def visit_FunctionDef(self, node):
		body = node.body
		http_method = ''
		try:
			if hasattr(node, 'decorator_list'):
				http_method = node.decorator_list[0].keywords[0].value.elts[0].s
		except Exception:
			pass
		functionNode = Node(attributes={'type': 'function', 'name': node.name, 'start_line': body[0].lineno,
		                                'end_line': _get_last_line_number(body), 'docstring': ast.get_docstring(node),
		                                'http': http_method},
		                    parent=self._parentNode)
		self._functions.append(functionNode)
		
		oldParent = self._parentNode
		self._parentNode = functionNode
		ast.NodeVisitor.generic_visit(self, node)
		self._parentNode = oldParent
	
	def visit_ClassDef(self, node):
		body = node.body
		classNode = Node(attributes={'type': 'class', 'name': node.name, 'start_line': body[0].lineno,
		                             'end_line': _get_last_line_number(body), 'docstring': ast.get_docstring(node)},
		                 parent=self._parentNode)
		self._classes.append(classNode)
		oldParent = self._parentNode
		self._parentNode = classNode
		ast.NodeVisitor.generic_visit(self, node)
		self._parentNode = oldParent


class ClassVisitor(ast.NodeVisitor):
	_classes = []
	
	def visit_ClassDef(self, node):
		body = node.body
		fields = []
		for statement in node.body:
			if isinstance(statement, ast.Assign):
				if len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
					stmt = str(statement.targets[0].id)
					if not (stmt.startswith('__')) and stmt != 'created_at' and stmt != 'update_at':
						if isinstance(statement.value, ast.Call):
							data = ast.dump(statement.value)
							if 'BigInteger' in data:
								data_type = 'Long'
							elif 'String' in data:
								data_type = 'String'
							elif 'DateTime' in data:
								data_type = 'Date'
							elif 'Text' in data:
								data_type = 'String'
							elif 'ForeignKey' in data:
								data_type = 'Long'
							elif 'Numeric' in data:
								data_type = 'Double'
							elif 'Boolean' in data:
								data_type = 'Boolean'
							else:
								data_type = '?'
						fields.append({'name': stmt, 'type': data_type})
					pass
				pass
		clazz = {node.name: {'fields': fields, 'start_line': body[0].lineno, 'end_line': _get_last_line_number(body)}}
		self._classes.append(clazz)
	
	@property
	def get_classes(self):
		return self._classes
