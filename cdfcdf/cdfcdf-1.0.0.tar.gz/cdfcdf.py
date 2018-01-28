"""""""print_lol"""""""
def print_lol_function(the_list):
   # """"""
   # ''''''
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol_function(each_item)
        else:
            print(each_item)
    #这个符号也是注释
