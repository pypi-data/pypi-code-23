import koliko_nester, sys
"""This is the "nester.py" module and it provides one function called print_lol()
    which prints list that may or may not include nested slits."""
def print_lol(this_list, indent=False,level=0,fh=sys.stdout):
    """This function take one positional argument called"the_list", which
        is any python list (of -possibl -nested lists)). Each data item in the
        provided list is (recursively) printed to the screen on it's own line."""
    for each_item in this_list:
        if isinstance(each_item,list):
            print_lol(each_item, level+1,fh)
        else:
            for stop_tab in range(level):
                print("\t",end='',file=fh)
            print(each_item,file=fh)
