#"""将列表中的元素打印出来"""

def print_list(the_list): #"""遍历各个表格"""
	for each_item in the_list:
		if isinstance(each_item,list):
			print_list(each_item)
		else:
			print(each_item)
