"""this is nester.py module, which include print_lol() function to test distribution"""

def print_lol(the_list):
	"""print every thing in a list included embeded list"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
