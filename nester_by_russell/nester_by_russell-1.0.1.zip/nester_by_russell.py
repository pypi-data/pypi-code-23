 def print_with_tab(the_list, incident=False, level = 0):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_with_tab(each_item, incident, level+1)
		else:
			if incident:
				for tab_stop in range(level):
					print("\t", end='')
			print(each_item)
