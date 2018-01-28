from visitor import AnalysisNodeVisitor
import ast
import json
def main():
	buf = open('/home/kiditz/slerp_io/api/learning_material_api.py', 'r')
	tree = ast.parse(buf.read())
	buf.close()
	visitor = AnalysisNodeVisitor()
	visitor.visit(tree)
	for f in visitor.functions:
		print(json.loads(f.attributes['docstring']))
	pass
	

if __name__ == '__main__':
	main()