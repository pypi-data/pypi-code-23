"""this is the huaji_nester.py module """

def print_lol(the_list, indent = False, level = 0):
    #the function ...
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1)
        else:
            if indent:
                print('\t' * level, end = '')
            print('-', end = '')
            print(each_item)
