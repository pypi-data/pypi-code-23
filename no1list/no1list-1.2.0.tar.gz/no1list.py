import sys

movie = [1,[2,2],3,[4,4,[5,5]]]
'''This the nested.py module, and it provides one function called print_lol() which prints lists that may or may not included nested list'''
def print_lol(list1,indent = False ,level = 0,fh = sys.stdout):

	for each_item in list1:
		if isinstance(each_item,list):
			print_lol(each_item, indent , level+1,filename)
		else:
			if indent:
				for _  in range(level):
					print('\t',end = '',file = fh)

			print(each_item,file = fh)

