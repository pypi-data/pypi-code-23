import sys
movie = ['123','456','789',['abc','def','ghi','jkm',['q1w2e3','a1s2d3']]]
'''This the nested.py module, and it provides one function called print_lol() which prints lists that may or may not included nested list'''
def print_lol(list1):

	for each_item in list1:
		if isinstance(each_item,list):
			print_lol(each_item)
		else:
			print(each_item)
print_lol(movie)

