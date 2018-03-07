""" This is "nester.py" module which provides a function
named 'print_lol' to print lists that may or may not contain
nested lists. """
def print_lol(the_list):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)