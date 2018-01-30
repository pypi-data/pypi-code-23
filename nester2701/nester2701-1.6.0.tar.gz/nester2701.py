import sys

def print_lol(the_list, indent=False, level=0, data_file=sys.stdout):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1, data_file)
        else:
            if indent:
                for tab_space in range(level):
                    print('\t', end='', file=data_file) #aqui só imprime o tab
            print(each_item, file=data_file)
           
