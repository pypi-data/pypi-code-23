import sys

def print_lol(the_list, indent=False, level=0, fh=sys.stdout) :
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1, fh)
        else:
            if indent:
                for tab_space in range(level):
                    print('\t', end='', file=fh)
            print(each_item, file=fh)       

'''
lista = [1,2,3,4,[5,6,7,8,[7,8,9]]]
try:
    with open('man.txt', 'w') as man_file:
        print_lol(lista, True, 0, man_file)
except IOError as err:
    print('File error: ' + err)
'''
