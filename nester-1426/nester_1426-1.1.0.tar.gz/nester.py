
"""This is the "nester.py" module and it provides one function called print_lol()
which prints lists that may or may not include nested lists."""
def print_lol(the_list,indent=False,level=0):
    '''This function takes three arguments. 
        The first is called 'the_list', which is any Python list (of - possibly - nested lists).Each data item in the provided list is (recursively) printed to the screen on its own line.
        The second argument(named indent) is used to decide whether to insert tabs when there is a
        nested list.
        The third argument(named level) is used to decide how many tabs to be inserted.'''

    for each_item in the_list:
            if isinstance(each_item,list):
                    print_lol(each_item,indent,level+1)
            else:
                if indent:
                    print('\t'*level,end='')
                print(each_item)
