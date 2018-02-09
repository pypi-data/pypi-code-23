
"""
这是nester.py模块，提供了一个名为print_list（）的函数，这个函数的作用是打印列表，
其中有可能包含（可能不包含）嵌套列表
"""
'''
This is the "nester.py" module and it privdes one function called "print_list()"
which prints lists that may or may not include nested listed.
'''

def print_list (the_list):
    """
    这个函数去一个位置参数the_list，这可以是任何Python列表（也可以是包含嵌套列表的列表）。
    所指定的列表中的每个数据项会（递归地）输出到屏幕上，各数据项各占一行
    """
    '''
    This function takes one positional argument called "the_list", which is any Python
    list (of-possibly-nested lists).Each data item in the privided list is (recursicely)
    printed to the screen on it's own line.
    '''
    for each_item in the_list:
        if isinstance (each_item,list):
            print_list(each_item)
        else:
            print(each_item)
