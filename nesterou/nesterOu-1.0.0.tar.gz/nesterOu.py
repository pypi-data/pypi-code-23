def show_Print(the_list):
	for each in the_list:
		if isinstance(each,list):
			show_Print(each)
		else:
			print(each)
