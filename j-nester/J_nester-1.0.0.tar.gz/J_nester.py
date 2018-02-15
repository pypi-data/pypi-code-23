"""This is a standard way to include a multiline
comment in your code"""
def print_lol(the_list):
    """这个函数取值，参数是列表类型，输出一个数据一行"""
def print_lol(the_list):
 for each_item in the_list:
  if isinstance(each_item,list):
   print_lol(each_item)
  else:
   print(each_item)
